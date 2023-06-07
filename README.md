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

https://github.com/marketplace?type=actions


Environment Variables:
1. echo "Commit ID: "  $GITHUB_SHA
2. echo "Repository Name:"  $GITHUB_REPOSITORY
3. echo "Workspace directory:"  $GITHUB_WORKSPACE
4. echo "Token for authentication." ${{ github.token }}
5. $GITHUB_REF : Branch we pushed in to.
---------------------------------------------------------------------------------------------------------------------------------------
When we make a Pull request we are running github actions as if the code is merged. 
https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows

Reference for CronJobs:  (minimum: each 5 mins)
https://crontab.guru/ [cron: minutes hours dayOfMonth Month DayOfTheWeek]
https://crontab.guru/examples.html

1 * * * *

1,2 * * * *

1-3 * * * *

0/15 * * * *        Runs every 15 minutes starting from minute 0

20/15 * * * *       Runs every 15 minutes starting from minute 20

0  * * * *          Every hour

0 12 * AUG *

0 12 * AUG 0        [ 0 - Sunday ] 
---------------------------------------------------------------------------------------------------------------------------------------
Repositoty Dispatch Event:
https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#repository_dispatch
Trigger workflow in one repository from another. Trigger a workflow from application.

 curl -X POST -H "Accept: application/vnd.github+json" -H "Authorization: Bearer xxxxxxxxxxxxxx" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/repos/user_name/githubActionsTest/dispatches -d '{"event_type":"build", "client_payload":{"unit":false,"integration":true}}'


---------------------------------------------------------------------------------------------------------------------------------------
Run workflow only on certain branches / certain file changes. 
https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#filter-pattern-cheat-sheet

cannot use 
branches, branches-ignore

tags, tags-ignore

paths, paths-ignore

both options at the same time. 

*: Matches zero or more characters, but does not match the / character. For example, Octo* matches Octocat.

**: Matches zero or more of any character.

?: Matches zero or one of the preceding character.

+: Matches one or more of the preceding character.

[] Matches one character listed in the brackets or included in ranges. Ranges can only include a-z, A-Z, and 0-9. For example, the range[0-9a-z] matches any digit or lowercase letter. For example, [CB]at matches Cat or Bat and [1-2]00 matches 100 and 200.

!: At the start of a pattern makes it negate previous positive patterns. It has no special meaning if not the first character.


---------------------------------------------------------------------------------------------------------------------------------------
Environment Variables: 
https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables

${{ secrets.GITHUB_TOKEN }}
https://docs.github.com/en/actions/security-guides/automatic-token-authentication

https://docs.github.com/en/actions/using-jobs/assigning-permissions-to-jobs

---------------------------------------------------------------------------------------------------------------------------------------
Usage of large encrypted secrets. 
https://docs.github.com/en/actions/security-guides/encrypted-secrets#storing-large-secrets
A secret can only be in size of 64 Kb. 
GPG Download Links  -  https://gnupg.org/ https://gnupg.org/download/index.html
GPG command to encrypt       gpg --symmetric --cipher-algo AES256 test.json
---------------------------------------------------------------------------------------------------------------------------------------
Contexts: example github, secrets, steps etc 

https://docs.github.com/en/actions/learn-github-actions/contexts

---------------------------------------------------------------------------------------------------------------------------------------
Expression Functions: https://docs.github.com/en/actions/learn-github-actions/expressions#functions 

Status check functions: https://docs.github.com/en/actions/learn-github-actions/expressions#status-check-functions
---------------------------------------------------------------------------------------------------------------------------------------

