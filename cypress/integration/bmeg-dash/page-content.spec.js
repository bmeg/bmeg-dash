// test a failing callback

const baseURL = Cypress.config("baseURL"); 

describe("Page content tests", () => {

  it("returns expected payloads", () => {
    const payload = {
      output: "page-content.children",
      outputs: { id: "page-content", property: "children" },
      inputs: [{ id: "url", property: "pathname" }],
      changedPropIds: [],
    };
    cy.request("POST", `${baseURL}/_dash-update-component`, payload).then(
      (response) => {
        // discover this response structure by using browser's devtools
        console.log(response.body)  
        expect(response.status, "Should return a 200").to.eq(200);
      }
    );
  });
 
});
