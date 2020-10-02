describe("Home Page Tests", () => {

  before(() => {
    // runs once before all tests in the block
    cy.visit("http://localhost:8050");

  });

  it("Has expected sidebar static content", () => {
    cy.contains("A graph database");
    cy.contains("Home");
    cy.contains("TCGA Clustering");
    cy.contains("Literature Gene-Compound Associations");
    cy.contains("Cancer Compound Screening");
    cy.contains("Gene-level Mutation View");
    cy.contains("Pathway View");
    cy.get("#sidebar-toggle")
  });

  it("Has expected home page content", () => {
    cy.contains("Tumor vs. Normal");
    cy.contains("Curated Literature Evidence");
    cy.contains("Identify Compound Treatment Candidates from Cancer Cell Line Compound Screens");
    cy.contains("Explore Mutations");
    cy.contains("Pathways");  
  });

  it("Has expected home page plot", () => {
    cy.get(".svg-container");
  });


});
