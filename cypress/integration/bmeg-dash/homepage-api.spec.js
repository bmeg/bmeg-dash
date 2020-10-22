// test the homepage callback

const baseURL = Cypress.config("baseURL"); 

describe("Home Page API Tests", () => {

  it("Has expected vertex counts", () => {
    const payload = {
        output: "cards.children",
        outputs: { id: "cards", property: "children" },
        inputs: [{ id: "url", property: "pathname", value: "/" }],
        changedPropIds: [],
    };
    const expected_results = {
        " Alleles": 6809815,
        " Genes": 63677,
        " Proteins": 104619,
        " Transcripts": 214804,
        " Pathways": 4794,
        " Compounds": 10683,
        " Drug Responses": 632413,
        " Interactions": 2068995,
        " Exons": 737019,
        " Aliquots": 170713,
        " Projects": 67,
        " PubLit Articles": 29162966
    }

    cy.request("POST", `${baseURL}/_dash-update-component`, payload).then(
      (response) => {
        // cy.log(JSON.stringify(response.body))
        cy.log(JSON.stringify(expected_results));
        expect(response.status, "Should return a 200").to.eq(200);
        const data = response.body.response.cards.children[0].props.figure.data;
        expect(
          Object.keys(expected_results).length,
          "Should return data for expected results"
        ).to.eq(data.length);
        data.forEach((d) => {
          const expected_result = expected_results[d.number.suffix];
          expect(expected_result, `${d.number.suffix}`).to.be.at.least(d.value);
        });
      }
    );

  });

});
