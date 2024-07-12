concaveHull = function () {
    let calcDist = stdevDist
    let padding = 0
    let voronoi
    const dist = (a, b) => ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    function stdevDist(voronoi) {
        const sides = new Array(voronoi.length * 3)
        voronoi.forEach((d, i) => {
            sides[i * 3 + 0] = dist(d[0], d[1])
            sides[i * 3 + 1] = dist(d[0], d[2])
            sides[i * 3 + 2] = dist(d[1], d[2])
        })
        return d3.mean(sides) + d3.deviation(sides)
    }

    function concaveHull(vertices) {
        voronoi = d3.voronoi().triangles(vertices)
        const long = calcDist(voronoi)
        const mesh = voronoi.filter(d => dist(d[0], d[1]) < long && dist(d[0], d[2]) < long && dist(d[1], d[2]) < long)
        const counts = {}
        const edges = {}
        let r
        const result = []

        // Traverse the edges of all triangles and discard any edges that appear twice.
        mesh.forEach(triangle => {
            for (let i = 0; i < 3; i++) {
                const edge = [triangle[i], triangle[(i + 1) % 3]].sort(ascendingCoords).map(String);
                (edges[edge[0]] = (edges[edge[0]] || [])).push(edge[1]);
                (edges[edge[1]] = (edges[edge[1]] || [])).push(edge[0]);
                var k = edge.join(":")
                if (counts[k]) delete counts[k]
                else counts[k] = 1
            }
        })

        while (true) {
            let k = null
            // Pick an arbitrary starting point on a boundary.
            for (k in counts) break
            if (k === null) break
            result.push(r = k.split(":").map(d => d.split(",").map(Number)))
            delete counts[k]
            let q = r[1]
            while (q[0] !== r[0][0] || q[1] !== r[0][1]) {
                const p = q
                const qs = edges[p.join(",")]
                const n = qs.length
                for (let i = 0; i < n; i++) {
                    q = qs[i].split(",").map(Number)
                    const edge = [p, q].sort(ascendingCoords).join(":")
                    if (counts[edge]) {
                        delete counts[edge]
                        r.push(q)
                        break
                    }
                }
            }
        }

        return padding !== 0 ? pad(result, padding) : result
    }

    function pad(bounds, amount) {
        return bounds.map(bound => {
            // http://forums.esri.com/Thread.asp?c=2&f=1718&t=174277
            const handedness = bound.map((p, i) => {
                const pm = bound[i === 0 ? bound.length - 1 : i - 1]
                return (p[0] - pm[0]) * (p[1] + pm[1]) * 0.5
            }).reduce((a, b) => a + b) > 0 ? -1 : 1

            return bound.map((p, i) => {
                const normal = rotate(tan(p, bound[i === 0 ? bound.length - 2 : i - 1]), 90 * handedness)
                return [p[0] + normal.x * amount, p[1] + normal.y * amount]
            })
        })
    }

    function tan(a, b) {
        const vec = { x: b[0] - a[0], y: b[1] - a[1] }
        const mag = Math.sqrt(vec.x * vec.x + vec.y * vec.y)
        vec.x /= mag
        vec.y /= mag
        return vec
    }

    function rotate(vec, angle) {
        angle *= Math.PI / 180
        return {
            x: vec.x * Math.cos(angle) - vec.y * Math.sin(angle),
            y: vec.x * Math.sin(angle) + vec.y * Math.cos(angle)
        }
    }

    const ascendingCoords = (a, b) => a[0] === b[0] ? b[1] - a[1] : b[0] - a[0]

    concaveHull.padding = function (newPadding) {
        if (!arguments.length) return padding
        padding = newPadding
        return concaveHull
    }

    concaveHull.distance = function (newDist) {
        if (!arguments.length) return calcDist
        calcDist = typeof newDist === "number" ? () => newDist : newDist
        return concaveHull
    }

    return concaveHull
}