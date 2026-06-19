function renderEcoGrafo(data) {
  const svg = d3.select("#eco-grafo");
  svg.selectAll("*").remove();
  const width = svg.node().clientWidth;
  const height = 600;

  const simulation = d3.forceSimulation(data.nodes || [])
    .force("link", d3.forceLink(data.links || []).id(d => d.id).distance(80))
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(20));

  const link = svg.append("g")
    .attr("stroke", "#94a3b8")
    .attr("stroke-opacity", 0.6)
    .selectAll("line")
    .data(data.links || [])
    .join("line")
    .attr("stroke-width", d => Math.sqrt(d.peso || 1));

  const node = svg.append("g")
    .attr("stroke", "#1a2138")
    .attr("stroke-width", 1.5)
    .selectAll("circle")
    .data(data.nodes || [])
    .join("circle")
    .attr("r", d => 8 + (d.centralidade || 0) * 12)
    .attr("fill", d => d.suspeita_bot ? "#dc2626" : "#4285F4");

  node.append("title").text(d => `${d.id} (${d.tipo})${d.suspeita_bot ? ' - suspeita bot' : ''}`);

  const label = svg.append("g")
    .attr("font-family", "system-ui, sans-serif")
    .attr("font-size", 11)
    .attr("fill", "#1a2138")
    .selectAll("text")
    .data(data.nodes || [])
    .join("text")
    .text(d => d.id)
    .attr("text-anchor", "middle")
    .attr("dy", d => -(10 + (d.centralidade || 0) * 12));

  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);
    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);
    label
      .attr("x", d => d.x)
      .attr("y", d => d.y);
  });
}
