
function fixed_layout(svg_id, data, min, max, hl_nodes, hl_groups) {

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
        .call(node => node.append("title").text(d => d.id))

    if (hl_nodes_map) {
        // let i = 0
        // for (let id of hl_nodes_map) {
        //     node_link_container.selectAll("circle").filter(d => id == d.id).classed(`highlight node${i % 4}`, true)
        //     i++
        // }
        node_link_container.selectAll("circle").filter(d => hl_nodes_map.has(d.id)).classed('highlight', true)
        node_link_container.selectAll("circle").sort((d => hl_nodes_map.has(d.id) ? 1 : -1))
    }
    
    if (hl_groups_map) {
        node_link_container.selectAll("circle").filter(d => hl_groups_map.has(d.group)).classed('highlight', true)
        node_link_container.selectAll("circle").sort((d => hl_groups_map.has(d.group) ? 1 : -1))
    }
      
    node_link_container.selectAll("circle")
        .on("mouseover", function(event, d) {
            if (d.selected == undefined || d.selected == false) {
                highlight(d)
                d.selected = false
            }
        })
        .on("mouseout", function(event, d) {
            if (d.selected == undefined || d.selected == false) {
                unhighlight(d)
                d.selected = false
            }
        })
        .on("click", function(event, d) {
            // clear_highlight()
            // highlight(d)
            // d.selected = true
            send_clear_highlight_event()
            send_highlight_event(d.id)
        })
    
        svg.on("click", function(event, d) {
            const clickedElement = event.target;
            
            if (clickedElement.tagName != "circle") {
                // clear_highlight()
                send_clear_highlight_event()
            }
        })
    
        const HIGHLIGHT_NODE_EVENT = "highlight_node"
        const CLEAR_HIGHLIGHT_EVENT = "clear_highlight"

        function send_highlight_event(id) {
            const customEvent = new CustomEvent(HIGHLIGHT_NODE_EVENT, {
                detail: { nodeID: id }
            })
            document.dispatchEvent(customEvent)
        }

        function send_clear_highlight_event() {
            const customEvent = new CustomEvent(CLEAR_HIGHLIGHT_EVENT)
            document.dispatchEvent(customEvent)
        }

        document.addEventListener(HIGHLIGHT_NODE_EVENT, function (event) {
            const { nodeID } = event.detail;
            let node_data = id2node.get(nodeID)
            if (node_data != null) {
                highlight(id2node.get(nodeID))
                id2node.get(nodeID).selected = true
            }
        })

        document.addEventListener(CLEAR_HIGHLIGHT_EVENT, function (event) {
            clear_highlight()
        })

        function highlight(d) {
            neighbors_links = node2edge.get(d.id)

            // node_link_container.selectAll("line").filter(link => neighbors_links.includes(link)).classed('hover_highlight', true)
            
            let new_ele = node_link_container
                .append("g")
                .attr("id", `${svg_id}_new_ele_${d.id}`)
            
            new_ele
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
                
            new_ele
                .selectAll("g")
                .data([d])
                .enter()
                .append("circle")
                .attr("cx", d => xScale(d.x))
                .attr("cy", d => yScale(d.y))
                .classed('hover_highlight', true)
                .style('pointer-events', 'none');
        }

        function unhighlight(d) {            
            // neighbors_links = node2edge.get(d.id)

            // node_link_container.selectAll("line").filter(link => neighbors_links.includes(link)).classed('hover_highlight', false)

            node_link_container.selectAll(`g#${svg_id}_new_ele_${d.id}`).remove();
        }

        function clear_highlight() {
            svg.selectAll("circle").each(function(d) {
                if (d.selected != undefined || d.selected == true) {
                    unhighlight(d)
                    d.selected = false
                }
            })
        }
}
