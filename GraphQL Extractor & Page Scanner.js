// ==UserScript==
// @name         GraphQL Extractor & Page Scanner (Generic)
// @namespace    http://tampermonkey.net/
// @version      0.3
// @description  Intercept GraphQL requests and scan page content for embedded queries on any site for introspection or research purposes.
// @author       Petec0x0
// @include      http://localhost:5013/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function () {
    'use strict';

    // SETTINGS *://*mywebsite*/*
    const ENABLE_REQUEST_LOGGING = true;
    const ENABLE_PAGE_SCANNING = true;

    const loggedOperations = new Set();

    // -------------------------
    // INTERCEPT FETCH
    // -------------------------
    if (ENABLE_REQUEST_LOGGING) {
        const originalFetch = window.fetch;
        window.fetch = async function (...args) {
            const [resource, config] = args;

            if (typeof resource === 'string' && resource.toLowerCase().includes('graphql')) {
                try {
                    const requestBody = config?.body;
                    const body = typeof requestBody === 'string' ? JSON.parse(requestBody) : requestBody;
                    if (Array.isArray(body)) body.forEach(logQuery);
                    else logQuery(body);
                } catch (e) {
                    console.error('[GraphQL Extractor] Fetch parse error:', e);
                }
            }

            return originalFetch.apply(this, args);
        };
    }

    // -------------------------
    // INTERCEPT XHR
    // -------------------------
    if (ENABLE_REQUEST_LOGGING) {
        const originalOpen = XMLHttpRequest.prototype.open;
        const originalSend = XMLHttpRequest.prototype.send;

        XMLHttpRequest.prototype.open = function (method, url) {
            this._isGraphQL = url.toLowerCase().includes('graphql');
            return originalOpen.apply(this, arguments);
        };

        XMLHttpRequest.prototype.send = function (body) {
            if (this._isGraphQL) {
                try {
                    const parsed = JSON.parse(body);
                    if (Array.isArray(parsed)) parsed.forEach(logQuery);
                    else logQuery(parsed);
                } catch (e) {
                    console.error('[GraphQL Extractor] XHR parse error:', e);
                }
            }
            return originalSend.apply(this, arguments);
        };
    }

    // -------------------------
    // LOGGING FUNCTION
    // -------------------------
    function logQuery(operation) {
        if (!operation || typeof operation !== 'object') return;

        const { operationName, query, variables } = operation;
        const id = JSON.stringify(operation);

        if (loggedOperations.has(id)) return;
        loggedOperations.add(id);

        console.group(`[GraphQL Extractor] ${operationName || '(unnamed)'}`);
        console.log('Operation Name:', operationName);
        console.log('Query:', query);
        console.log('Variables:', variables);
        console.groupEnd();
    }

    // -------------------------
    // PAGE SCANNING FUNCTIONS
    // -------------------------
    function searchAllScriptsForGraphQL() {
        const scripts = Array.from(document.querySelectorAll('script, pre, code'));
        const graphqlRegex = /(?:query|mutation)\s+\w+\s*\([^\)]*\)\s*{[\s\S]*?}/gm;

        scripts.forEach((el, i) => {
            const content = el.textContent;
            if (!content || content.length < 50) return;
            const matches = content.match(graphqlRegex);
            if (matches) {
                matches.forEach((match, j) => {
                    if (!loggedOperations.has(match)) {
                        loggedOperations.add(match);
                    }
                    console.group(`[GraphQL Extractor] Found query in script #${i}, match ${j + 1}`);
                    console.log(match.slice(0, 500));
                    console.groupEnd();
                });
            }
        });
    }

    function searchJSONScriptTags() {
        const scripts = document.querySelectorAll('script[type="application/json"]');
        scripts.forEach((script, index) => {
            try {
                const data = JSON.parse(script.textContent);
                const str = JSON.stringify(data);
                if (str.includes('query') || str.includes('mutation')) {
                    if (!loggedOperations.has(str)) {
                        loggedOperations.add(str);
                    }
                    console.group(`[GraphQL Extractor] JSON script #${index} contains GraphQL-like data`);
                    console.log(data);
                    console.groupEnd();
                }
            } catch (e) {
                // ignore
            }
        });
    }

    function scanRawHTML() {
        const html = document.documentElement.innerHTML;
        const graphqlRegex = /(?:query|mutation)\s+\w+\s*\([^\)]*\)\s*{[\s\S]*?}/gm;
        const matches = html.match(graphqlRegex);
        if (matches) {
            console.group('[GraphQL Extractor] Found raw GraphQL fragments in HTML');
            matches.forEach((match, i) => {
                if (!loggedOperations.has(match)) {
                    loggedOperations.add(match);
                }
                console.log(`[${i + 1}] ${match.slice(0, 500)}`);
            });
            console.groupEnd();
        }
    }

    // -------------------------
    // RUN PAGE SCANNERS
    // -------------------------
    if (ENABLE_PAGE_SCANNING) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                searchAllScriptsForGraphQL();
                searchJSONScriptTags();
                scanRawHTML();
            }, 1000); // Give the DOM a moment to fully load
        });
    }

    // -------------------------
    // SAVE TO FILE FEATURE
    // -------------------------

    function saveQueriesToFile() {
        if (!loggedOperations.size) {
            alert("No GraphQL operations captured yet.");
            return;
        }

        const blob = new Blob(Array.from(loggedOperations).map(op => op + "\\n\\n"), {
            type: "text/plain"
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "graphql_queries.txt";
        a.click();

        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    // Trigger save on Ctrl+Shift+S
    window.addEventListener("keydown", function (e) {
        if (e.ctrlKey && e.shiftKey && e.code === "KeyS") {
            saveQueriesToFile();
        }
    });
})();
