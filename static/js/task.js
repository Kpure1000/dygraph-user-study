var SELECT_NODE_EVENT = 'select_node';
var UNSELECT_NODE_EVENT = 'unselect_node';
var TAG_NODE_EVENT = 'tag_node';
var UNTAG_NODE_EVENT = 'untag_node';

function add_radio_listener() {
    $('#r-group').find('input[type=radio]').change(function() {
        let q1 = $('#r-group').find('input[type=radio]:checked').val();

        let q2_container = $('#q2-container');
        
        let q2_number = $('#q2-number');
        let q2_number_hint_increase = $('#increase-hint');
        let q2_number_hint_decrease = $('#decrease-hint');
        
        if (q1 != null) {
            let q2_input = q2_container.find('input[type=number]')
            switch (q1) {
                case 'increase':
                    q2_container.slideDown({duration: 200});
                    q2_input.prop('required', true);
                    q2_number.prop('min', 0.01);
                    q2_number.prop('max', 0.99);
                    q2_number_hint_increase.slideDown({duration: 200});
                    q2_number_hint_decrease.slideUp({duration: 200});
                    break;
                case 'decrease':
                    q2_container.slideDown({duration: 200});
                    q2_input.prop('required', true);
                    q2_number.prop('min', 1.01);
                    q2_number.prop('max', 5.00);
                    q2_number_hint_increase.slideUp({duration: 200});
                    q2_number_hint_decrease.slideDown({duration: 200});
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

var selected_set = [NaN, NaN, NaN]

function add_selected_listener() {
    
    document.addEventListener(SELECT_NODE_EVENT, function (event) {
        const { id } = event.detail;

        let top_radio = $('#r-group').find('input[type=radio]:checked')
        let top_num = top_radio.val()

        if (selected_set.includes(id)) {
            alert("请勿重复选择节点")
        } 
        else if (top_num != null) {

            $(`label[for=${top_radio.attr('id')}]`).find('span').text(id)

            top_radio.find('span').val("" + id)
            let tagNodeEvent = null
            switch (top_num) {
                case 'top1':
                    $('#top1_answer').val(id)
                    selected_set[0] = id
                    tagNodeEvent = new CustomEvent(TAG_NODE_EVENT, {
                        detail: {tagID: 1, nodeID: id}
                    })
                    break;
                case 'top2':
                    // TODO
                    $('#top2_answer').val(id)
                    selected_set[1] = id
                    tagNodeEvent = new CustomEvent(TAG_NODE_EVENT, {
                        detail: {tagID: 2, nodeID: id}
                    })
                    break;
                case 'top3':
                    // TODO
                    $('#top3_answer').val(id)
                    selected_set[2] = id
                    tagNodeEvent = new CustomEvent(TAG_NODE_EVENT, {
                        detail: {tagID: 3, nodeID: id}
                    })
                    break;
                default:
                    break;
            }
            
            tagNodeEvent ? document.dispatchEvent(tagNodeEvent) : null

            if ($('#top1_answer').val() != '' && $('#top2_answer').val() != '' && $('#top3_answer').val() != '') {
                $('#submit_button').prop('disabled', false)
            }
        }
        else {
            alert("请先在右侧top列表中选中一个元素")
        }

    })

    document.addEventListener(UNSELECT_NODE_EVENT, function (event) {
        
        let top_radio = $('#r-group').find('input[type=radio]:checked')
        let top_num = top_radio.val()

        if (top_num != null) {
            $(`label[for=${top_radio.attr('id')}]`).find('span').text("")
            tagID = NaN
            nodeID = NaN
            switch (top_num) {
                case 'top1':
                    tagID = 1
                    nodeID = selected_set[0]
                    $('#top1_answer').val('')
                    selected_set[0] = NaN
                    break;
                case 'top2':
                    tagID = 2
                    nodeID = selected_set[1]
                    $('#top2_answer').val('')
                    selected_set[1] = NaN
                    break;
                case 'top3':
                    tagID = 3
                    nodeID = selected_set[2]
                    $('#top3_answer').val('')
                    selected_set[2] = NaN
                    break;
                default:
                    break;
            }

            if (!isNaN(tagID) && !isNaN(nodeID)) {
                tagNodeEvent = new CustomEvent(UNTAG_NODE_EVENT, {
                    detail: {tagID: tagID, nodeID: nodeID}
                })
                document.dispatchEvent(tagNodeEvent)
            }

            $('#submit_button').prop('disabled', true)

        }

    })
}

$(document).ready(function() {
    
    $.ajax({
        url: '/get-data',
        type: 'GET',
        success: function(data) {
            start_task(data)
        },
        error: function(xhr, status, error) {
            alert(`获取数据失败，详细信息: ${xhr.responseJSON.error}`)
        },
    })
})

function start_task(data) {
    $.ajax({
        url: '/start-task',
        type: 'GET',
        success: function() {
            $("#loading-animation").hide();
            $('#slices-container').show();
            
            $('#current_uid').text(data["uid"])
            $('#current_task').text(data["cur_task"] + 1)
            let cur_method = data["cur_method"]
            let task_type = data["task_type"]
            vis_data = data["data"]
            let hl_slices = null
            let hl_nodes = null
            let hl_groups = null
            if (task_type === 1) {
                // hl_nodes = vis_data["highlight-nodes"]
                hl_slices = vis_data["highlight-slices"]

                add_selected_listener();
            } else {
                hl_groups = vis_data["highlight-groups"]
                hl_slices = vis_data["highlight-slices"]

                add_radio_listener();
            }
            
            hl_slices = hl_slices.sort((a, b) => a - b)
            
            $('#time-slices-text').text("t" + (hl_slices[0] + 1) + ", " + "t" + (hl_slices[1] + 1));
            $('#time-slices-text-1').text("t" + (hl_slices[1] + 1));
            $('#time-slices-text-2').text("t" + (hl_slices[0] + 1));

            if (hl_groups != null) {
                $('#a-cluster').css("display", hl_groups.length == 1 ? "inline" : "none")
                $('#double-cluster').css("display", hl_groups.length == 2 ? "inline" : "none")
            }
            
            hl_slices = new Set(hl_slices)
            
            let data_slices = vis_data["timeslices"]
            let ulist = $("#slices")
            
            let total_nodes = []
            
            // 高亮时间片中共有的节点
            let intersected_nodes = data_slices[hl_slices.values().next().value].nodes.map(node => node.id) 

            hl_slices.forEach(slice => {
                slice_nodes = data_slices[slice].nodes.map(node => node.id)
                intersected_nodes = intersected_nodes.filter(v => slice_nodes.includes(v))
            });

            intersected_nodes = new Set(intersected_nodes)

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
            
            let node_extand = global_normalize(total_nodes)
            for (let i = 0; i < data_slices.length; i++) {
                if (cur_method === "incremental")
                    node_extand = local_normalize(data_slices[i].nodes);
                is_highlight = hl_slices.has(i)
                fixed_layout(`slice${i + 1}`, data_slices[i], node_extand.min, node_extand.max, hl_nodes, hl_groups, is_highlight, intersected_nodes)
            }
            
        },
        error: function(xhr, status, error) {
            alert(`开始任务失败，详细信息: ${xhr.responseJSON.error}`)
        },
    })

}

function local_normalize(nodes) {
    xval = d3.extent(nodes, d => d.x)
    yval = d3.extent(nodes, d => d.y)

    console.log("xmin=" + xval[0], "xmax=" + xval[1], "ymin=" + yval[0], "ymax=" + yval[1])

    let center = {x: (xval[0] + xval[1]) * 0.5, y: (yval[0] + yval[1]) * 0.5}
    let scale = Math.max((xval[1] - xval[0]) * 0.5, (yval[1] - yval[0]) * 0.5)
    
    return {
        min: {x: center.x - scale, y: center.y - scale},
        max: {x: center.x + scale, y: center.y + scale}
    }
}

function global_normalize(nodess) {
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
