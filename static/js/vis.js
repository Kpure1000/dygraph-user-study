
function fixed_layout(svg_id, data, min, max, hl_nodes, hl_groups) {

    let svg = d3.select('#' + svg_id)

    let nodes = data.nodes;
    let links = data.links;
    
    const padding = 10

    let svgRect = svg.node().getBoundingClientRect();

    const xScale = d3.scaleLinear().domain([min.x, max.x]).range([padding, svgRect.width - padding]);
    const yScale = d3.scaleLinear().domain([min.y, max.y]).range([svgRect.height - padding, padding]);

    let get_group_color = d3.scaleOrdinal(d3.schemeCategory10)
    // let get_group_color = ()=>{return "#E6E6E7"}

    let id2node = new Map(nodes.map(node => [node.id, node]));

    let link = svg.append("g")
        .attr("stroke", "#E6E7E7")
        .attr("stroke-opacity", 0.4)
        .attr("stroke-width", 1.9)
        .selectAll("line")

    let node = svg.append("g")
        .attr("stroke", "#9FA0A0")
        .attr("stroke-width", 1.5)
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
        .attr("fill", d => get_group_color(d.group))
        .on("mosueouver", function(d){  
            console.log(d);
        })
        .on("mosueout", function(d){  
            console.log(d);
        })
        .attr("cx", d => xScale(d.x))
        .attr("cy", d => yScale(d.y))
        .attr("fill", "#aaa")
        .attr("r", 2)

}
