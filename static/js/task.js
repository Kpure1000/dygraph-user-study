
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
                    q2_input.val(0);
                    break;
                default:
                    break;
            }
        }
    })
}


function layout_normalize(nodess) {
    let xmin = Number.MAX_VALUE, ymin = Number.MAX_VALUE,
        xmax = Number.NEGATIVE_INFINITY, ymax = Number.NEGATIVE_INFINITY
    for (let nodes in nodess) {
        for (let n in nodess[nodes]) {
            let node = nodess[nodes][n]
            xmin = Math.min(node.x, xmin)
            ymin = Math.min(node.y, ymin)
            xmax = Math.max(node.x, xmax)
            ymax = Math.max(node.y, ymax)
        }
    }
    
    let date_center_x = (xmin + xmax) * 0.5
    let date_center_y = (ymin + ymax) * 0.5
    let data_radius = Math.max(xmax - xmin, ymax - ymin) * 0.6
    let svg_radius = Math.min(rect.width, rect.height) * 0.5
    
    for (let nodes in nodess) {
        for (let n in nodess[nodes]) {
            let node = nodess[nodes][n]
            node.x -= date_center_x
            node.x = node.x * svg_radius / data_radius
            node.y -= date_center_y
            node.y = node.y * svg_radius / data_radius
        }
    }
}


$(document).ready(function() {
    
    add_radio_listener();

    $.ajax({
        url: '/get-data',
        type: 'GET',
        success: function(data) {
            console.log(data);
            
            $('#current_uid').text(data["uid"])
            $('#current_task').text(data["cur_task"] + 1)
            $('#total_task').text(data["total_task"])
            // TODO: 还没做这个分类
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
            console.log(hl_slices)
            
            let data_slices = vis_data["timeslices"]
            let ulist = $("#slices")
            
            let total_nodes = []
            let fixeds = []

            for (let i = 0; i < data_slices.length; i++) {
                total_nodes.push(data_slices[i].nodes)
                let color = "#666"
                if (hl_slices.has(i)) {
                    color = "#aaaacc"
                }
                ulist.append(`<li>
                        <svg style="border-color: ${color};" id="slice${i+1}"></svg>
                        <div style="text-align: center; color: ${color};">
                            <i id="slice_id">${i + 1}</i>
                        </div>
                </li>`)

                fixeds.push(new fix_layout(`slice${i+1}`))
    

            }

            rect = d3.select(`#slice1`).node().getBoundingClientRect();
            
            layout_normalize(total_nodes, rect)
            
            for (let i = 0; i < data_slices.length; i++) {
                fixeds[i].vis(data_slices[i], hl_nodes, hl_groups)
            }

            
        },
        error: function(xhr, status, error) {
            alert(`获取数据失败，详细信息: ${xhr.responseJSON.error}`)
        }
    })
})