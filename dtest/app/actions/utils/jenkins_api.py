import jenkinsapi
from jenkinsapi.jenkins import Jenkins
import datetime, requests

class jenkins_tools():
    chartdata = {}
    def __init__(self):
        jenkins_server_url = "http://10.101.66.12:8080/jenkins"
        user_id = "admin"
        api_token = "8d4243b37e47d73e612394578e49fa44"
        server = Jenkins(jenkins_server_url, username=user_id, password="admin517517")

    def conn_jenkins_server(self):
        try:
            jenkins_server_url = "http://10.101.66.12:8080/jenkins"
            user_id = "admin"
            api_token = "8d4243b37e47d73e612394578e49fa44"
            server = Jenkins(jenkins_server_url, username=user_id, password="admin517517")

            # job = server.get_job("H5 UI")
            # build = job.get_last_build()
            # print(build.get_result_url())
            # print(job.is_running())
            # print(job.is_enabled())
            # print(job.get_build_triggerurl())
            #response = server.requester.post_url(job.get_build_triggerurl())

            # print(server.items())
            # print(job.is_running())
            return server
        except Exception:
            return None

    def project_built(self, project_name):
        server = self.conn_jenkins_server()
        job = server.get_job(project_name)
        if job.is_running() == False:
            job.invoke()
        else:
            print(project_name + " is running")

    def stop_build(self, project_name):
        server = self.conn_jenkins_server()
        job = server.get_job(project_name)
        job.get_last_build().stop()

    def get_build_list(self,project_name):
        server = self.conn_jenkins_server()
        job = server.get_job(project_name)
        job_name = job.get_full_name()
        # first_build = job.get_first_buildnumber()
        last_build = job.get_last_buildnumber()

        listdic = {}
        build_list = []

        failed = []
        succ = []
        total = []
        builds = []

        for count in range(last_build, last_build -20 , -1):
            listdic.clear()
            try:
                count_build = job.get_build(count)
            except:
                print("build is not found")

            listdic["job"] = job_name
            listdic["build_number"] = count

            start_time = count_build.get_timestamp()
            adjust_time = start_time + datetime.timedelta(hours=8)
            listdic["build_time"] = adjust_time.strftime("%Y-%m-%d %H:%M:%S")

            listdic["status"] = count_build.get_status()

            result_url = count_build.get_result_url()
            response_get = requests.get(result_url).content

            totalCount = response_get[response_get.index("totalCount\":") + 12:response_get.index(",\"urlName")]

            response_get = response_get[response_get.index("\"result\":"):len(response_get)]
            listdic["result"] = response_get

            fail_count = response_get[response_get.index("failCount\":") + 11:response_get.index(",\"passCount")]
            pass_count = response_get[response_get.index("passCount\":") + 11:response_get.index(",\"skipCount")]

            builds.append(count)
            failed.append(fail_count)
            succ.append(pass_count)
            total.append(totalCount)

            build_list.append(listdic.copy())

        builds.reverse()
        failed.reverse()
        succ.reverse()
        total.reverse()
        self.chartdata["builds"] = builds
        self.chartdata["failed"] = failed
        self.chartdata["succ"] = succ
        self.chartdata["total"] = total

        print(self.chartdata)
        print(build_list)

        return build_list

    def is_job_running(self, project_name):
        server = self.conn_jenkins_server()
        job = server.get_job(project_name)
        if job.is_running():
            return True
        else:
            return False


