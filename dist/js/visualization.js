//$(document).ready( function () {
const nodeFilterSelector = document.getElementById("nodeFilterSelect");
const edgeFilters = document.getElementsByName("edgesFilter");
const nodeFilterSelector2 = document.getElementById("nodeFilterSelect2");



function startNetwork(data) {
  const container = document.getElementById("mynetwork");
  const options = {
    edges: {
      //           length: 400 // Longer edges between nodes.
    },
    physics: {
      // Even though it's disabled the options still apply to network.stabilize().
      enabled: true,
      solver: "repulsion",
      repulsion: {
        nodeDistance: 200 // Put more distance between the nodes.
      }
    }
  };
  new vis.Network(container, data, options);
  //  network.stabilize();
}

/**
 * filter values are updated in the outer scope.
 * in order to apply filters to new values, DataView.refresh() should be called
 */
let nodeFilterValue = "";
let params = new URLSearchParams(location.search);

if (params.get("topic") != "") {
  nodeFilterValue = params.get("topic");

}

const edgesFilterValues = {
  binding_req: true,
  binding_req: true,
  binding_ext: true,
  binding_pref: true,
  binding_exm: true,
  extension: true,
  contains: true,
  values_from: true,
  system: true,
  logical_model_from: true,
  transaction: true,
  questionnaire: true

};

/*
filter function should return true or false
based on whether item in DataView satisfies a given condition.
*/
const nodesFilter = (node) => {
  if (nodeFilterValue === "") {
    return true;
  }
  switch (nodeFilterValue) {
    case "Profile":
      return node.type === "Profile";
    case "Extension":
      return node.type === "Extension";
    case "CodeSystem":
      return node.type === "CodeSystem";
    case "ValueSet":
      return node.type === "ValueSet";
    case "LogicalModel":
      return node.type === "LogicalModel";
    case "Transaction":
      return node.type === "Transaction";
    case "Questionnaire":
      return node.type === "Questionnaire";
      
    case "Vaccination":
      return node.topic === "Vaccination";
    case "Core":
      return node.topic === "Core";
    case "Terminology":
      return node.topic === "Terminology";
    case "Addiction":
      return node.topic === "Addiction";
    case "Problem":
      return node.topic === "Problem";
    case "Medication":
      return node.topic === "Medication";
    case "Allergy_Intolerance":
      return node.topic === "Allergy_Intolerance";
    case "Home_Care":
      return node.topic === "Home_Care";
    case "Patient_Will":
      return node.topic === "Patient_Will";
    case "Score_Result":
      return node.topic === "Score_Result";
    case "Referral_Prescription":
      return node.topic === "Referral_Prescription";
    default:
      return true;
  }
};

var _nodes = new vis.DataSet();
var _edges = new vis.DataSet();


var data = {
  nodes: _nodes,
  edges: _edges,
};

$.getJSON('../data/edges.json', function (edges) {
  _edges.add(edges);
});
$.getJSON('../data/nodes.json', function (nodes) {
  _nodes.add(nodes);
});

const edgesFilter = (edge) => {
  return edgesFilterValues[edge.relation];
};

const nodesView = new vis.DataView(_nodes, { filter: nodesFilter });
const edgesView = new vis.DataView(_edges, { filter: edgesFilter });

nodeFilterSelector.addEventListener("change", (e) => {
  // set new value to filter variable
  nodeFilterValue = e.target.value;
  /*
  refresh DataView,
  so that its filter function is re-calculated with the new variable
*/
  nodesView.refresh();
});

nodeFilterSelector2.addEventListener("change", (e) => {
  // set new value to filter variable
  nodeFilterValue = e.target.value;
  /*
  refresh DataView,
  so that its filter function is re-calculated with the new variable
*/
  nodesView.refresh();
});

edgeFilters.forEach((filter) =>
  filter.addEventListener("change", (e) => {
    const { value, checked } = e.target;
    edgesFilterValues[value] = checked;
    edgesView.refresh();
  })
);
startNetwork({ nodes: nodesView, edges: edgesView });
//startNetwork({ nodes: nodesView, edges: edgesView });
//});

