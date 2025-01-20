
function fixed_layout(svg_id, data, min, max, hl_nodes, hl_groups, is_highlight_slice, intersected_nodes) {

    let svg = d3.select('#' + svg_id)

    let nodes = data.nodes;
    let links = data.links;
    
    const padding = 10

    let svgRect = svg.node().getBoundingClientRect();

    const xScale = d3.scaleLinear().domain([min.x, max.x]).range([padding, svgRect.width - padding]);
    const yScale = d3.scaleLinear().domain([min.y, max.y]).range([svgRect.height - padding, padding]);

    let hl_nodes_map = null
    if (hl_nodes != null) {
        hl_nodes_map = new Set(hl_nodes.map(id => id));
    }
    
    let hl_groups_map = null
    if (hl_groups != null) {
        hl_groups_map = new Set(hl_groups.map(id => id));
    }

    let id2node = new Map(nodes.map(node => [node.id, node]));

    let node2edge = new Map(nodes.map(node => [node.id, []]));

    links.forEach(link => {
        node2edge.get(link.source).push(link);
        node2edge.get(link.target).push(link);
    })

    let node_link_container = svg.append("g")
    node_link_container.attr("id", `${svg_id}_node_link_container`)

    let node_tag_container = svg.append("g")
    node_tag_container.attr("id", `${svg_id}_tag_container`)

    let link = node_link_container.append("g").attr("id", `${svg_id}_link_container`)
        .selectAll("line")

    let node = node_link_container.append("g").attr("id", `${svg_id}_node_container`)
        .selectAll("circle")

        
    link = link
        .data(links)
        .enter()
        .append("line")
        .attr("x1", d => xScale(id2node.get(d.source).x))
        .attr("y1", d => yScale(id2node.get(d.source).y))
        .attr("x2", d => xScale(id2node.get(d.target).x))
        .attr("y2", d => yScale(id2node.get(d.target).y))

    node = node
        .data(nodes)
        .enter()
        .append("circle")
        .attr("cx", d => xScale(d.x))
        .attr("cy", d => yScale(d.y))
        .classed('not_allowed', d => is_highlight_slice ? !intersected_nodes.has(d.id) : true)
        .attr("cursor", d => is_highlight_slice ? intersected_nodes.has(d.id) ? "pointer" : "not-allowed" : "auto")
        .call(node => node.append("title").text(d => `${d.id}` + (d.group != undefined ? `[${d.group}]` : "")))

    if (hl_nodes_map) {
        // node_link_container.selectAll("circle").filter(d => hl_nodes_map.has(d.id)).classed('highlight', true)
        // node_link_container.selectAll("circle").sort((d => hl_nodes_map.has(d.id) ? 1 : -1))
    }
    
    if (hl_groups_map) {

        const colorGroup = d3.scaleOrdinal(d3.schemeCategory10).domain(Array.from(hl_groups_map));

        for (let group_id of hl_groups_map) {

            // node_link_container.selectAll("circle").filter(d => group_id == d.group).classed('highlight', true)
            // node_link_container.selectAll("circle").sort((d => group_id == d.group ? 1 : -1))
            
            const groupNodes = nodes.filter(d => group_id == d.group)
            if (groupNodes.length == 0)
                continue;

            new Promise((resolve, reject) => {
                const vertices = groupNodes.map(node => [xScale(node.x), yScale(node.y)]);
                    
                // let xval = d3.extent(groupNodes, d => d.x)
                // let yval = d3.extent(groupNodes, d => d.x)
                // let xmin = Number.MAX_VALUE, ymin = Number.MAX_VALUE, xmax = Number.NEGATIVE_INFINITY, ymax = Number.NEGATIVE_INFINITY
                // xmin = xScale(Math.min(xval[0], xmin))
                // ymin = yScale(Math.min(yval[0], ymin))
                // xmax = xScale(Math.max(xval[1], xmax))
                // ymax = yScale(Math.max(yval[1], ymax))
                // // let max_distance = Math.sqrt((xmax - xmin) * (xmax - xmin), (ymax - ymin) * (ymax - ymin))
                // let max_distance = Math.max(xmax - xmin, ymax - ymin)

                const hullGenerater = concaveHull().distance(65).padding(4);
    
                const hull_vertices_paths = hullGenerater(vertices); // 这是一个二维数组, 每个元素是一个path的坐标数组
                
                resolve(hull_vertices_paths);
            }).then(hull_vertices_paths => {
                const curve = d3.line()
                .x(d => d[0])
                .y(d => d[1])
                .curve(d3.curveCatmullRom);
                // .curve(d3.curveLinear);

                node_link_container.append("g").attr("class", "hull")
                    .selectAll("path")
                    .data(hull_vertices_paths) 
                    .enter()
                    .append("path") 
                    .attr("d", (d) => curve(d))
                    .attr("stroke", (d) => colorGroup(group_id))
                    .style('pointer-events', 'none');
            })
            
        }

    }

    if (is_highlight_slice) {
        node_link_container.selectAll("circle")
            .filter((d)=>intersected_nodes.has(d.id))
            .on("mouseover", function(event, d) {
                if (d.selected == undefined || d.selected == false) {
                    send_clear_highlight_event(false)
                    send_highlight_event(d.id, false)
                }
            })
            .on("mouseout", function(event, d) {
                if (d.selected == undefined || d.selected == false) {
                    send_clear_highlight_event(false)
                }
            })
            .on("click", function(event, d) {
                send_clear_highlight_event(true)
                send_highlight_event(d.id, true)
            })
    
        svg.on("click", function(event, d) {
                const clickedElement = event.target;
                
                if (clickedElement.tagName != "circle") {
                    send_clear_highlight_event(true)
                }
            })
    }
    
        const HIGHLIGHT_NODE_EVENT = "highlight_node"
        const CLEAR_HIGHLIGHT_EVENT = "clear_highlight"

        function send_highlight_event(id, is_selected) {
            const customEvent = new CustomEvent(HIGHLIGHT_NODE_EVENT, {
                detail: { nodeID: id , selected: is_selected}
            })
            document.dispatchEvent(customEvent)

            if (is_selected) {
                const selectEvent = new CustomEvent(SELECT_NODE_EVENT, {
                    detail: {id: id}
                })
                document.dispatchEvent(selectEvent)
            }
            
        }

        function send_clear_highlight_event(clear_selected) {
            const customEvent = new CustomEvent(CLEAR_HIGHLIGHT_EVENT, {
                detail: { clear_selected: clear_selected}
            })
            document.dispatchEvent(customEvent)

            if (clear_selected) {
                const unselectEvent = new CustomEvent(UNSELECT_NODE_EVENT)
                document.dispatchEvent(unselectEvent)
            }
        }

        document.addEventListener(HIGHLIGHT_NODE_EVENT, function (event) {
            const { nodeID, selected } = event.detail;
            let node_data = id2node.get(nodeID)
            if (node_data != null) {
                id2node.get(nodeID).selected = selected
                highlight(id2node.get(nodeID))
            }
        })

        document.addEventListener(CLEAR_HIGHLIGHT_EVENT, function (event) {
            const { clear_selected } = event.detail;
            svg.selectAll("circle").each(function(d) {
                if (d.selected != undefined) {
                    if (clear_selected) {
                        unhighlight(d)
                        d.selected = false
                    } else if (d.selected == false) {
                        unhighlight(d)
                    }
                }
            })
        })

        document.addEventListener(TAG_NODE_EVENT, function (event) {
            const { tagID, nodeID } = event.detail;
            let node_data = id2node.get(nodeID)
            if (node_data != null) {
                showNodeTag(tagID, node_data)
            }
        })

        document.addEventListener(UNTAG_NODE_EVENT, function (event) {
            const { tagID, nodeID } = event.detail;
            let node_data = id2node.get(nodeID)
            if (node_data != null) {
                removeNodeTag(tagID)
            }
        })

        function showNodeTag(tagID, d) {

            console.log('show tag', tagID, d.id)

            let top_tag = node_tag_container
                    .append("g")
                    .attr("id", `${svg_id}_new_ele_${tagID}`)
                
            top_tag.selectAll("g")
                .data([d])
                .enter()
                .append("text")
                .attr("x", d => xScale(d.x))
                .attr("y", d => yScale(d.y))
                .text(tagID)
                .style('pointer-events', 'none');
        }

        function removeNodeTag(tagID) {

            console.log('remove tag', tagID)

            node_tag_container.select(`#${svg_id}_new_ele_${tagID}`).remove()
        }

        function highlight(d) {
            neighbors_links = node2edge.get(d.id)

            let top_elements = node_link_container
                .append("g")
                .attr("id", `${svg_id}_new_ele_${d.id}`)
            
            top_elements
                .selectAll("g")
                .data(neighbors_links)
                .enter()
                .append("line")
                .attr("x1", d => xScale(id2node.get(d.source).x))
                .attr("y1", d => yScale(id2node.get(d.source).y))
                .attr("x2", d => xScale(id2node.get(d.target).x))
                .attr("y2", d => yScale(id2node.get(d.target).y))
                .classed('hover_highlight', true)
                .style('pointer-events', 'none');
                
            top_elements
                .selectAll("g")
                .data([d])
                .enter()
                .append("circle")
                .attr("cx", d => xScale(d.x))
                .attr("cy", d => yScale(d.y))
                .classed('highlight', d.selected) //hl_nodes_map != null && hl_nodes_map.has(d.id))
                .classed('hover_highlight', true)
                .style('pointer-events', 'none');
        }

        function unhighlight(d) {
            node_link_container.selectAll(`g#${svg_id}_new_ele_${d.id}`).remove();
        }

}
