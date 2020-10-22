// test the gene dropdown callback

const baseURL = Cypress.config("baseURL"); 

describe("Gene autocomplete API Tests", () => {


  it("autocompletes symbol", () => {
    const payload = {
      output: "gene_dd.options",
      outputs: { id: "gene_dd", property: "options" },
      inputs: [{ id: "gene_dd", property: "search_value", value: "BRC" }],
      changedPropIds: ["gene_dd.search_value"],
    };

    cy.request("POST", `${baseURL}/_dash-update-component`, payload).then(
      (response) => {
        expect(response.status, "Should return a 200").to.eq(200);
        // discover this response structure by using browser's devtools
        const keys = Object.keys(response.body.response);
        expect(keys, `Should contain expected keys`).to.contain("gene_dd");
        expect(
          response.body.response.gene_dd.options.length,
          `Should return expected suggestions`
        ).to.eq(5);
      }
    );
  });


  it("returns expected payloads", () => {
    const payload = {
      output:
        "..evd.children...resp_histo.children...pie_taxon.children...occr.children..",
      outputs: [
        { id: "evd", property: "children" },
        { id: "resp_histo", property: "children" },
        { id: "pie_taxon", property: "children" },
        { id: "occr", property: "children" },
      ],
      inputs: [
        { id: "gene_dd", property: "value", value: "MTOR/ENSG00000198793" },
      ],
      changedPropIds: [],
    };
    cy.request("POST", `${baseURL}/_dash-update-component`, payload).then(
      (response) => {
        expect(response.status, "Should return a 200").to.eq(200);

        // discover this response structure by using browser's devtools
        const keys = Object.keys(response.body.response);
        expect(keys, `Should contain expected keys`).to.contain("evd");
        expect(keys, `Should contain expected keys`).to.contain("occr");
        expect(keys, `Should contain expected keys`).to.contain("pie_taxon");
        expect(keys, `Should contain expected keys`).to.contain("resp_histo");
      }
    );
  });


 
});
