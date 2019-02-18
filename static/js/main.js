$(document).ready(function() {
    console.log('js script');

    $('.btn btn-warning').on('click', function() {
    console.log('hey there')
    //  $.ajax({
    //    url: '/plan_4G',
    ////    data: { type: $(this).data('type') },
    //    method: 'GET'
    //  })
    //  .done((res) => {
    //    getStatus(res.data.task_id)
    //  })
    //  .fail((err) => {
    //    console.log(err)
    //  });
    });

    function getStatus(taskID) {
      $.ajax({
        url: `/status/${taskID}`,
        method: 'GET'
      })
      .done((res) => {
        const html = `
          <tr>
            <td>${res.data.task_id}</td>
            <td>${res.data.task_status}</td>
    //        <td>${res.data.task_result}</td>
          </tr>`
        $('#tasks').prepend(html);
        const taskStatus = res.data.task_status;
        if (taskStatus === 'finished' || taskStatus === 'failed') return false;
        setTimeout(function() {
          getStatus(res.data.task_id);
        }, 2000);
      })
      .fail((err) => {
        console.log(err);
      });
    }
}
