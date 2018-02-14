/**
 * Created by jintingting on 2017/11/27.
 */

function autoadd(id, type){
            console.log('/openapi/autoadd/');
            $.post("/openapi/autoadd/",
                {
                    "id": id,
                    "type":type
                },
                function(res) {


                }
            )
        }