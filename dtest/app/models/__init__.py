#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math import ceil

from flask import request
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Query
from werkzeug.exceptions import abort

from dtest import settings
from dtest.app.helpers import DotDict


class Pagination(object):
    """Internal helper class returned by :meth:`BaseQuery.paginate`.  You
    can also construct it from any other SQLAlchemy query object if you are
    working with other libraries.  Additionally it is possible to pass `None`
    as query object in which case the :meth:`prev` and :meth:`next` will
    no longer work.
    """

    def __init__(self, query, page, page_size, total, items):
        #: the unlimited query object that was used to create this
        #: pagination object.
        self.query = query
        #: the current page number (1 indexed)
        self.page = page
        #: the number of items to be displayed on a page.
        self.page_size = page_size
        #: the total number of items matching the query
        self.total = total
        #: the items for the current page
        self.items = items

    @property
    def pages(self):
        """The total number of pages"""
        if self.page_size == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.page_size)))
        return pages

    def prev(self, error_out=False):
        """Returns a :class:`Pagination` object for the previous page."""
        assert self.query is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.query.paginate(self.page - 1, self.page_size, error_out)

    @property
    def prev_num(self):
        """Number of the previous page."""
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        assert self.query is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.query.paginate(self.page + 1, self.page_size, error_out)

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        if not self.has_next:
            return None
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides.  Skipped page numbers are represented as `None`.
        This is how you could render such a pagination in the templates:
        .. sourcecode:: html+jinja
            {% macro render_pagination(pagination, endpoint) %}
              <div class=pagination>
              {%- for page in pagination.iter_pages() %}
                {% if page %}
                  {% if page != pagination.page %}
                    <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
                  {% else %}
                    <strong>{{ page }}</strong>
                  {% endif %}
                {% else %}
                  <span class=ellipsis>…</span>
                {% endif %}
              {%- endfor %}
              </div>
            {% endmacro %}
        """
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or (self.page - left_current - 1 < num < self.page + right_current) or \
                            num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


class BaseQuery(Query):
    def first_or_404(self):
        """Like :meth:`first` but aborts with 404 if not found instead of returning ``None``."""

        rv = self.first()
        if rv is None:
            abort(404)
        return rv

    def get_scalar(self, column):
        scalar_query = (self.statement.with_only_columns([column])
                        .order_by(None))
        return self.session.execute(scalar_query).scalar()

    def count_star(self):
        return self.get_scalar(func.count())

    def paginate(self, page=None, page_size=None, error_out=True):
        """Returns ``page_size`` items from page ``page``.
        If no items are found and ``page`` is greater than 1, or if page is
        less than 1, it aborts with 404.
        This behavior can be disabled by passing ``error_out=False``.
        If ``page`` or ``page_size`` are ``None``, they will be retrieved from
        the request query.
        If the values are not ints and ``error_out`` is ``True``, it aborts
        with 404.
        If there is no request or they aren't in the query, they default to 1
        and 20 respectively.
        Returns a :class:`Pagination` object.
        """

        if request:
            if page is None:
                try:
                    if 'page' in request.view_args:
                        page = int(request.view_args['page'])
                    else:
                        page = int(request.args.get('page', 1))
                except (TypeError, ValueError):
                    if error_out:
                        abort(404)
                    page = 1

            if page_size is None:
                try:
                    if 'page_size' in request.view_args:
                        page_size = int(request.view_args['page_size'])
                    else:
                        page_size = int(request.args.get('page_size', 20))
                except (TypeError, ValueError):
                    if error_out:
                        abort(404)
                    page_size = 20
        else:
            if page is None:
                page = 1
            if page_size is None:
                page_size = 20

        if error_out and page < 1:
            abort(404)

        # No need to execute the query if page_size == 0
        if page_size == 0:
            items = []
        else:
            items = self.limit(page_size).offset((page - 1) * page_size).all()

        if not items and page != 1 and error_out:
            abort(404)

        # No need to count if we're on the first page and there are fewer
        # items than we expected.
        if page == 1 and len(items) < page_size:
            total = len(items)
        else:
            total = self.count_star()

        return Pagination(self, page, page_size, total, items)


class ORMClass(object):
    _json_column_list = None
    _json_column_exclude_list = ['update_time']
    _json_column_display_all_relations = False

    def __str__(self):
        return unicode(self).encode('utf-8')

    def scaffold_list_columns(self):
        """
            Return a list of columns from the model.
        """
        columns = []

        for p in self._sa_class_manager.mapper.iterate_properties:
            if hasattr(p, 'direction'):
                if self._json_column_display_all_relations or p.direction.name == 'MANYTOONE':
                    columns.append(p.key)
            elif hasattr(p, 'columns'):
                if len(p.columns) > 1:
                    continue
                else:
                    column = p.columns[0]

                if column.foreign_keys:
                    continue

                columns.append(p.key)

        return columns

    def get_list_columns(self):
        """
            Returns a list of the model field names. If `column_list` was
            set, returns it. Otherwise calls `scaffold_list_columns`
            to generate the list from the model.
        """
        columns = self._json_column_list

        if columns is None:
            columns = self.scaffold_list_columns()

            # Filter excluded columns
            if self._json_column_exclude_list:
                columns = [c for c in columns if c not in self._json_column_exclude_list]

        return columns

    @classmethod
    def get(cls, _id):
        return cls.query.get(_id)

    @classmethod
    def get_or_404(cls, _id):
        if _id is None:
            abort(404)
        rv = cls.query.get(_id)
        if rv is None:
            abort(404)
        return rv

    def to_json(self, columns=None):
        columns = columns or self.get_list_columns()
        j = DotDict({})
        for c in columns:
            if hasattr(self, c):
                j[c] = getattr(self, c)
            elif '__' in c:
                attrs = c.split('__')
                p = self
                for attr in attrs:
                    if hasattr(p, attr):
                        p = getattr(p, attr)
                    elif attr in p:
                        p = p[attr]
                    else:
                        p = None
                    j[c] = p
                    if p is None:
                        break
            else:
                j[c] = None
        return j

    def save(self, commit=True, flush=False):
        db_session.add(self)
        if commit:
            db_session.commit()
        elif flush:
            db_session.flush()
        return self

    def delete(self, commit=True):
        db_session.delete(self)
        if commit:
            db_session.commit()


engine = create_engine(settings.DB_CONNECT_STRING,
                       convert_unicode=True,
                       pool_recycle=1800,
                       echo=settings.DB_SQL_ECHO,
                       max_overflow=30)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Model = declarative_base(name='Model', cls=ORMClass)
Model.query = db_session.query_property(BaseQuery)


def __init_db():
    Model.metadata.create_all(bind=engine)


def merge_model(instance):
    if not instance:
        return
    if instance not in db_session:
        instance = db_session.merge(instance)
    return instance


def with_session(fn):
    def go(*args, **kw):
        db_session.begin(subtransactions=True)
        try:
            ret = fn(*args, **kw)
            db_session.commit()
            return ret
        except:
            db_session.rollback()
            raise

    return go


if __name__ == '__main__':
    __init_db()
