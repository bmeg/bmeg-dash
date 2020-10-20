// test the RNA expression callback

describe("RNA Expression API Tests", () => {

  const expected_projects = [
    "Project:CCLE",
    "Project:GTEx_Adipose Tissue",
    "Project:GTEx_Adrenal Gland",
    "Project:GTEx_Bladder",
    "Project:GTEx_Blood",
    "Project:GTEx_Blood Vessel",
    "Project:GTEx_Brain",
    "Project:GTEx_Breast",
    "Project:GTEx_Cervix Uteri",
    "Project:GTEx_Colon",
    "Project:GTEx_Esophagus",
    "Project:GTEx_Fallopian Tube",
    "Project:GTEx_Heart",
    "Project:GTEx_Kidney",
    "Project:GTEx_Liver",
    "Project:GTEx_Lung",
    "Project:GTEx_Muscle",
    "Project:GTEx_Nerve",
    "Project:GTEx_Ovary",
    "Project:GTEx_Pancreas",
    "Project:GTEx_Pituitary",
    "Project:GTEx_Prostate",
    "Project:GTEx_Salivary Gland",
    "Project:GTEx_Skin",
    "Project:GTEx_Small Intestine",
    "Project:GTEx_Spleen",
    "Project:GTEx_Stomach",
    "Project:GTEx_Testis",
    "Project:GTEx_Thyroid",
    "Project:GTEx_Uterus",
    "Project:GTEx_Vagina",
    "Project:TCGA-ACC",
    "Project:TCGA-BLCA",
    "Project:TCGA-BRCA",
    "Project:TCGA-CESC",
    "Project:TCGA-CHOL",
    "Project:TCGA-COAD",
    "Project:TCGA-DLBC",
    "Project:TCGA-ESCA",
    "Project:TCGA-GBM",
    "Project:TCGA-HNSC",
    "Project:TCGA-KICH",
    "Project:TCGA-KIRC",
    "Project:TCGA-KIRP",
    "Project:TCGA-LAML",
    "Project:TCGA-LGG",
    "Project:TCGA-LIHC",
    "Project:TCGA-LUAD",
    "Project:TCGA-LUSC",
    "Project:TCGA-MESO",
    "Project:TCGA-OV",
    "Project:TCGA-PAAD",
    "Project:TCGA-PCPG",
    "Project:TCGA-PRAD",
    "Project:TCGA-READ",
    "Project:TCGA-SARC",
    "Project:TCGA-SKCM",
    "Project:TCGA-STAD",
    "Project:TCGA-TGCT",
    "Project:TCGA-THCA",
    "Project:TCGA-THYM",
    "Project:TCGA-UCEC",
    "Project:TCGA-UCS",
    "Project:TCGA-UVM",
  ].sort();

  it("Has expected drop down values", () => {
    const payload = {"output":"page-content.children","outputs":{"id":"page-content","property":"children"},"inputs":[{"id":"url","property":"pathname","value":"/app/rna_umap"}],"changedPropIds":["url.pathname"]};
    cy.request('POST', "http://localhost:8050/app/_dash-update-component", payload).then((response) => {
      // cy.log(JSON.stringify(response.body)) ;
      expect(response.status, "Should return a 200").to.eq(200);

      // discover this response structure by using browser's devtools
      const data =
        response.body
        .response["page-content"]
        .children.props.children.props.children[0]
        .props.children[0].props.children[1].props.options;
      // cy.log(JSON.stringify(data));
      const actual_values = data.map((d) => d.value).sort();
      // cy.log(JSON.stringify(actual_values));
      const diff_values = actual_values.filter((x) => !expected_projects.includes(x));
      expect(diff_values.length, `Should have all expected values ${diff_values}`).to.eq(0);
    })
  });

  const testProject = (project, property) => {
    // test umap call back for a project
    // throws exception if problem

    const payload = {
      output: "umap_fig.children",
      outputs: { id: "umap_fig", property: "children" },
      inputs: [
        { id: "project_dd_tmn", property: "value", value: project },
        {
          id: "property_dd_tmn",
          property: "value",
          value: property,
        },
      ],
      changedPropIds: ["property_dd_tmn.value"],
    };

    cy.request(
        "POST",
        "http://localhost:8050/app/_dash-update-component",
        payload
      )
      .then((response) => {
        expect(response.status, "Should return a 200").to.eq(200);
        const data =
          response.body.response.umap_fig.children.props.figure.data;
        expect(data, `${project} - should return data`).to.not.be.undefined;
        const series = data[0];
        expect(series, `${project} - should return series`).to.not.be.undefined;

        const x = series.x;
        const y = series.y;
        expect(
          x.length,
          `${project} - X & Y should be same length`
        ).to.be.eq(y.length);
        expect(
          x.length,
          `${project} - to have at least one data point`
        ).to.be.gt(0);

      });
  };

  expected_projects.forEach((project) => {
    const property = "$c._data.cellline_attributes.Primary Disease";
    it(`${project} should return a series.`, () => testProject(project, property));
  } ) ;

});
