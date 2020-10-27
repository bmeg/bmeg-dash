# Testing

Browser level tests leverage [Cypress](https://www.cypress.io/features)

## Developing new tests

* first install the cypress package

```
npm install cypress --save-dev
```

* create or edit tests

```
ls -lR cypress/integration
```

* set test host

```
# see ./cypress.json
{
    "baseURL": "https://bmeg.io/app"
}
```


* interactively running tests

```
$(npm bin)/cypress open
```

## Running tests without the browser

```
./cypress-headless-tests.sh
```

