import json
import sys

def extract_data(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    nodes = []
    links = []
    
    for operation_key, operation in data.items():
        operation_name = operation['name']
        if {'id': operation_name, 'type': 'operation'} not in nodes:
            nodes.append({'id': operation_name, 'type': 'operation'})
        for ingredient in operation.get('ingredients', []):
            ingredient_name = ingredient['name']
            if not any(node['id'] == ingredient_name for node in nodes):
                nodes.append({'id': ingredient_name, 'type': 'ingredient'})
            try:
                if 'amount' in ingredient:
                    amount = ingredient['amount']
                elif 'amount_min' in ingredient and 'amount_max' in ingredient:
                    amount = (ingredient['amount_min'] + ingredient['amount_max']) / 2
                else:
                    raise ValueError("Amount information is missing")
                links.append({'source': ingredient_name, 'target': operation_name, 'value': amount})
            except Exception as e:
                print(f"Error processing ingredient in operation '{operation_name}': {ingredient}")
                raise e
        for product in operation.get('products', []):
            product_name = product['name']
            if not any(node['id'] == product_name for node in nodes):
                nodes.append({'id': product_name, 'type': 'product'})
            try:
                if 'amount' in product:
                    amount = product['amount']
                elif 'amount_min' in product and 'amount_max' in product:
                    amount = (product['amount_min'] + product['amount_max']) / 2
                else:
                    raise ValueError("Amount information is missing")
                links.append({'source': operation_name, 'target': product_name, 'value': amount})
            except Exception as e:
                print(f"Error processing product in operation '{operation_name}': {product}")
                raise e
    
    return nodes, links

def generate_html(nodes, links, output_file):
    with open(output_file, 'w') as file:
        file.write("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    .links line {
        stroke: #999;
        stroke-opacity: 0.6;
    }
    .nodes circle {
        stroke: #000;
        stroke-width: 1.5px;
    }
    text {
        font-family: Arial, sans-serif;
        font-size: 10px;
    }
</style>
</head>
<body>
<script src="https://d3js.org/d3.v5.min.js"></script>
<script>
var nodes = %s;
var links = %s;
var width = window.innerWidth, height = window.innerHeight;
var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height)
    .call(d3.zoom().on("zoom", function () {
        svg.attr("transform", d3.event.transform)
    }))
    .append("g");
var simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(function(d) { return d.id; }).distance(50))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2));
var link = svg.append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(links)
    .enter().append("line")
    .attr("stroke-width", function(d) { return Math.sqrt(d.value); });
var node = svg.append("g")
    .attr("class", "nodes")
    .selectAll("g")
    .data(nodes)
    .enter().append("g")
var circles = node.append("circle")
    .attr("r", 5)
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));
var labels = node.append("text")
    .text(function(d) { return d.id; })
    .attr('x', 6)
    .attr('y', 3);
node.append("title")
    .text(function(d) { return d.id; });
simulation
    .nodes(nodes)
    .on("tick", ticked);
simulation.force("link")
    .links(links);
function ticked() {
    link
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
    node
        .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
}
function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}
function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}
function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}
</script>
</body>
</html>
""" % (json.dumps(nodes), json.dumps(links)))
        print(f"Generated HTML file: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py input.json output.html")
        sys.exit(1)
    
    input_json, output_html = sys.argv[1], sys.argv[2]
    nodes, links = extract_data(input_json)
    # Increase the number of iterations or reduce the cooling rate by adjusting parameters of simulation
    generate_html(nodes, links, output_html)

