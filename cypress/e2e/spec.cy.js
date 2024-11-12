describe('My First Test', () => {
  const username = "admin"
  const password = "password"
  beforeEach(function () {
    // login before each test
    cy.loginByForm(username, password)
  })
  it('autofills slug field', () => {
    cy.visit('http://127.0.0.1:8000/admin/demo_sections/article/add/')
    cy.get('input#id_title').type("Asfd 1234")
    cy.wait(500)
    cy.get('input#id_slug').should('have.value', 'asfd-1234')

  })
})

