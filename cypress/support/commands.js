// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
Cypress.Commands.add('loginByForm', (username, password) => {
      Cypress.log({
        name: 'loginByForm',
        message: `${username} | ${password}`,
      })

      cy.visit('http://127.0.0.1:8000/admin/login/')
      cy.get('#id_username').type(username)
      cy.get('#id_password').type(password)
      cy.get('input[type="submit"]').click()
      cy.url().should('contain', '/admin/')

    })
