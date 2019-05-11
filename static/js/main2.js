$(document).ready(function() {
    var fileName = "";
    // plan button event
    $('.btn.btn-warning').click(function() {
      // check if the parameters are filled
      if ($('#rCol').val()!="" && $('#rMin').val()!=""){
          $.ajax({
            type: 'POST',
            url: "/plan_3G",
            data:$('#plan').serialize(),
            success: function(response){
                // check if there is job_id key within the json
                // console.log(response)
                rsp_json = JSON.parse(response)
                if (Object.keys(rsp_json).includes("job_id")){
                    job_id=rsp_json['job_id']
                    console.log('job id :'+job_id)
                    var pg = 0
                    setTimeout(function(){
                        var periodic_check = setInterval(function(){
                            getStatus(job_id,periodic_check)
                        },5000);
                    },5000);
                }else{
                    alert('Please check that you have uploaded your file!')
                }
            },
            error: function(error){
                console.log(error)
            }});
      }else{
        alert('Please check all plan parameters are given!')
      }
    });
    function getStatus(taskID,periodic_func){
        $.ajax({
            type: 'GET',
            url: "/results/" + taskID,
            contentType:'text/json; charset=utf-8',
            dataType:'json',
            success: function(response){
                console.log('log:' + JSON.stringify(response));
                // set the progress bar
                pg=response['meta']['progress'];
                updateProgressBar(pg);
                // update the log
                $('#statusLog').text('Status: '+response['status'])
                if (pg != 'undefined'){
                    $('#progressLog').text('Progress: ' + pg)
                }
                // if progress == 100, stop the process
                if (parseInt(pg) == 100) {
                    clearInterval(periodic_func);
                    // enable the download button
                    $('#downloadButton').removeAttr("disabled");
                    // record the file name
                    fileName = response['meta']['file_name']
                    $('#fileName').attr('value',fileName)
                    console.log(fileName)
                }},
            error: function(error){
                console.log(error)
            }
           });
    };
    function updateProgressBar(val){
        console.log('progress:' + val)
        $('#pgBar').attr('style','width: '+val+'%')
    };
});
