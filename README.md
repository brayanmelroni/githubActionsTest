# githubActionsTest
YAML
'>' new lines will be replaced by a space

'|' new lines will be preserved. 

Artifact :  A file generated by my job. [Download log archive]


Setting secrets for debugging.
https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/enabling-debug-logging 
ACTIONS_STEP_DEBUG = true
ACTIONS_RUNNER_DEBUG = true

In default case jobs will run parallelly. use needs: [run-shell-command] to run sequentially. 

Shells: 
https://dev.to/pwd9000/github-actions-all-the-shells-581h#:~:text=You%20can%20set%20the%20shell,temporary%20script%20at%20%7B0%7D%20.
https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsshell


Actions:
https://github.com/actions/hello-world-javascript-action
https://github.com/actions/checkout 
(Checkout to commit and pull code from there.)

