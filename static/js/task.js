
function add_radio_listener() {
    $('#r-group').find('input[type=radio]').change(function() {
        let q1 = $('#r-group').find('input[type=radio]:checked').val();

        let q2_container = $('#q2-container');
        
        if (q1 != null) {
            let q2_input = q2_container.find('input[type=number]')
            switch (q1) {
                case 'increase':
                    q2_container.slideDown({duration: 200});
                    q2_input.prop('required', true);
                    break;
                case 'decrease':
                    q2_container.slideDown({duration: 200});
                    q2_input.prop('required', true);
                    break;
                case 'none':
                    q2_container.slideUp({duration: 200, });
                    q2_input.prop('required', false);
                    q2_input.val("");
                    break;
                default:
                    break;
            }
        }
    })
}

$(document).ready(function() {
    
    add_radio_listener();

    $.ajax({
        url: '/get-data',
        type: 'GET',
        success: function(data) {
            $("#loading-animation").hide();
            $('#slices-container').show();
            
            $('#current_uid').text(data["uid"])
            $('#current_task').text(data["cur_task"] + 1)
            let task_type = data["task_type"]
            vis_data = data["data"]
            let hl_slices = null
            let hl_nodes = null
            let hl_groups = null
            if (task_type === 1) {
                hl_nodes = vis_data["highlight-nodes"]
                hl_slices = vis_data["highlight-slices"]
            } else {
                hl_groups = vis_data["highlight-groups"]
                hl_slices = vis_data["highlight-slices"]
            }
            
            hl_slices = new Set(hl_slices)
            
            let data_slices = vis_data["timeslices"]
            let ulist = $("#slices")
            
            let total_nodes = []
            
            for (let i = 0; i < data_slices.length; i++) {
                total_nodes.push(data_slices[i].nodes)
                highlight = hl_slices.has(i) ? "highlight" : ""
                ulist.append(`<li>
                        <svg id="slice${i+1}" ${highlight}></svg>
                        <div style="text-align: center; margin-bottom:15px;" ${highlight}>
                            t = ${i + 1}
                        </div>
                </li>`)
            }

            new Promise((resolve, reject) => {
                const node_extand = layout_normalize(total_nodes)
                for (let i = 0; i < data_slices.length; i++) {
                    fixed_layout(`slice${i + 1}`, data_slices[i], node_extand.min, node_extand.max, hl_nodes, hl_groups)
                }
                resolve('Graph drawn successfully');
            }).then(res => {
                //
            })

            
        },
        error: function(xhr, status, error) {
            alert(`获取数据失败，详细信息: ${xhr.responseJSON.error}`)
        },
    })
})

function layout_normalize(nodess) {
    let xmin = Number.MAX_VALUE, ymin = Number.MAX_VALUE,
        xmax = Number.NEGATIVE_INFINITY, ymax = Number.NEGATIVE_INFINITY
    for (let nodes in nodess) {
        xval = d3.extent(nodess[nodes], d => d.x)
        yval = d3.extent(nodess[nodes], d => d.y)
        xmin = Math.min(xval[0], xmin)
        ymin = Math.min(yval[0], ymin)
        xmax = Math.max(xval[1], xmax)
        ymax = Math.max(yval[1], ymax)
    }

    let center = {x: (xmin + xmax) * 0.5, y: (ymin + ymax) * 0.5}
    let scale = Math.max((xmax - xmin) * 0.5, (ymax - ymin) * 0.5)
    
    return {
        min: {x: center.x - scale, y: center.y - scale},
        max: {x: center.x + scale, y: center.y + scale}
    }
}
