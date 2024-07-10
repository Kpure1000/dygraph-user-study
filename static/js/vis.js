
// let selected_node_id = -1

class fix_layout {
    constructor(svg_id) {
        this.svg = d3.select('#' + svg_id)
    // 缩放比例尺
        let svgRect = this.svg.node().getBoundingClientRect();

        this.svg.attr("viewBox", [-svgRect.width / 2, -svgRect.height / 2, svgRect.width, svgRect.height])
    }

    clear()
    {
        this.svg.selectAll("*").remove()
    }
    
    vis(data, hl_nodes, hl_groups) {
        let nodes = data.nodes;
        let links = data.links;

        // ndoes list to dict and normalize nodes
        let nodes_dict = {}
        
        for (let n in nodes) {
            let node = nodes[n]
            nodes_dict[nodes[n].id] = node
        }

        let maxweight = 0
        for (let index = 0; index < links.length; index++) {
            let w = links[index].weight
            if (w > maxweight) maxweight = w
        }

        // let get_group_color = d3.scaleOrdinal(d3.schemeCategory20)
        let get_group_color = ()=>{return "#E6E6E7"}

        let link = this.svg.append("g")
            .attr("stroke", "#E6E7E7")
            .attr("stroke-opacity", 0.4)
            .attr("stroke-width", 1.9)
            .selectAll("line")

        let node = this.svg.append("g")
            .attr("stroke", "#9FA0A0")
            .attr("stroke-width", 1.5)
            .selectAll("circle")

        // let title = this.svg.append("g")
        //     .attr("font-size","3pt")
        //     .attr("fill", "#ccc")
        //     .attr("style", "user-select: none;")
        //     .style("font-weight", "bold")
        //     .style("text-anchor", "middle")
        //     .selectAll("text")
        
        // title = title
        //     .data(nodes)
        //     .enter()
        //     .append("text")
        //     .text(d=>d.id)
        //     .call(title => title.append("title").text(d => d.id + ', group: ' + d.group))
        //     .on("click", function(d){
        //         //
        //     })
        //     .attr("x",d=>d.x)
        //     .attr("y",d=>d.y)
        //     .attr("dy", 2)
        //     .attr("x",d=>d.x)
        //     .attr("y",d=>d.y)

        link = link
            .data(links)
            .enter()
            .append("line")
            .call(link => link.append("title").text(d => "(" + d.source + ", " + d.target + "), w: " + d.weight))
            .attr("x1", d => nodes_dict[d.source].x)
            .attr("y1", d => nodes_dict[d.source].y)
            .attr("x2", d => nodes_dict[d.target].x)
            .attr("y2", d => nodes_dict[d.target].y)

            node = node
            .data(nodes)
            .enter()
            .append("circle")
            .attr("fill", d => get_group_color(d.group))
            .on("click", function(d){
                //
                
            })
            .call(node => node.append("title").text(d => d.id + ', group: ' + d.group))
            .attr("cx", d => d.x)
            .attr("cy", d => d.y)
            .attr("fill", "#aaa")
            .attr("r", 2)

        // let scale = 1.0
        // let translate = { 'x': 0.0, 'y': 0.0 }

        // let svgRect = this.svg.node().getBoundingClientRect();

        // this.svg.call(d3.zoom()
        //     .extent([[0, 0], [svgRect.width, svgRect.height]])
        //     .scaleExtent([0.5, 6])
        //     .on('zoom', () => {
        //         //
        //     })
        // )

        // setInterval(() => {
        //     this.svg
        //         .selectAll('circle')
        //         .attr("fill", "#aaa")
        //         .attr("r", 2)

        //     title
        //         .attr("x", d => d.x * scale + translate.x)
        //         .attr("y", d => d.y * scale + translate.y)

        //     link
        //         .attr("x1", d => nodes_dict[d.source].x * scale + translate.x)
        //         .attr("y1", d => nodes_dict[d.source].y * scale + translate.y)
        //         .attr("x2", d => nodes_dict[d.target].x * scale + translate.x)
        //         .attr("y2", d => nodes_dict[d.target].y * scale + translate.y)

        //     node
        //         .attr("cx", d => d.x * scale + translate.x)
        //         .attr("cy", d => d.y * scale + translate.y)


        // }, 16)

    }

}
