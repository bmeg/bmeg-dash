describe("Home Page Tests", () => {

  before(() => {
    const baseURL = Cypress.config("baseURL"); 
    // runs once before all tests in the block
    cy.visit(baseURL);

  });

  it("Has expected sidebar static content", () => {
    cy.contains("BMEG Analysis");
    cy.contains("Home");
    cy.contains("RNA expression projection");
    cy.contains("Literature Gene-Compound Associations");
    cy.contains("Dose Response Comparisons");
    cy.contains("Gene-level Mutation View");
    cy.contains("Pathway View");
    cy.get("#sidebar-toggle")
  });

  it("Has expected home page content", () => {
    cy.contains("RNA expression projection");
    cy.contains("Curated Literature Evidence");
    cy.contains("Compare Dose Response of Compounds from Cancer Cell Line Screens");
    cy.contains("Gene-level Mutation View");
    cy.contains("Pathways");
  });

  it("Has expected home page plot", () => {
    cy.get(".svg-container");
  });


});
