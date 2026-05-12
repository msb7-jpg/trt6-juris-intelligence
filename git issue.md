# Dockerfile with a workspace project · Issue #6867 · astral-sh/uv

> The doc proposes the following Dockerfile to build a project into a Dockerfile while caching intermediate layers (uv version 0.4.0): # Install uv FROM python:3.12-slim COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv # Change the work...

[Skip to content](https://github.com/astral-sh/uv/issues/6867#start-of-content)

## Navigation Menu

Toggle navigation

[](https://github.com/)

[Sign in](https://github.com/login?return_to=https%3A%2F%2Fgithub.com%2Fastral-sh%2Fuv%2Fissues%2F6867)

Appearance settings

*   Platform
    
    *   AI CODE CREATION
        
        *   [
            
            GitHub CopilotWrite better code with AI
            
            ](https://github.com/features/copilot)
        *   [
            
            GitHub SparkBuild and deploy intelligent apps
            
            ](https://github.com/features/spark)
        *   [
            
            GitHub ModelsManage and compare prompts
            
            ](https://github.com/features/models)
        *   [
            
            MCP RegistryNewIntegrate external tools
            
            ](https://github.com/mcp)
        
    *   DEVELOPER WORKFLOWS
        
        *   [
            
            ActionsAutomate any workflow
            
            ](https://github.com/features/actions)
        *   [
            
            CodespacesInstant dev environments
            
            ](https://github.com/features/codespaces)
        *   [
            
            IssuesPlan and track work
            
            ](https://github.com/features/issues)
        *   [
            
            Code ReviewManage code changes
            
            ](https://github.com/features/code-review)
        
    *   APPLICATION SECURITY
        
        *   [
            
            GitHub Advanced SecurityFind and fix vulnerabilities
            
            ](https://github.com/security/advanced-security)
        *   [
            
            Code securitySecure your code as you build
            
            ](https://github.com/security/advanced-security/code-security)
        *   [
            
            Secret protectionStop leaks before they start
            
            ](https://github.com/security/advanced-security/secret-protection)
        
    *   EXPLORE
        
        *   [Why GitHub](https://github.com/why-github)
        *   [Documentation](https://docs.github.com/)
        *   [Blog](https://github.blog/)
        *   [Changelog](https://github.blog/changelog)
        *   [Marketplace](https://github.com/marketplace)
        
    
    [View all features](https://github.com/features)
    
*   Solutions
    
    *   BY COMPANY SIZE
        
        *   [Enterprises](https://github.com/enterprise)
        *   [Small and medium teams](https://github.com/team)
        *   [Startups](https://github.com/enterprise/startups)
        *   [Nonprofits](https://github.com/solutions/industry/nonprofits)
        
    *   BY USE CASE
        
        *   [App Modernization](https://github.com/solutions/use-case/app-modernization)
        *   [DevSecOps](https://github.com/solutions/use-case/devsecops)
        *   [DevOps](https://github.com/solutions/use-case/devops)
        *   [CI/CD](https://github.com/solutions/use-case/ci-cd)
        *   [View all use cases](https://github.com/solutions/use-case)
        
    *   BY INDUSTRY
        
        *   [Healthcare](https://github.com/solutions/industry/healthcare)
        *   [Financial services](https://github.com/solutions/industry/financial-services)
        *   [Manufacturing](https://github.com/solutions/industry/manufacturing)
        *   [Government](https://github.com/solutions/industry/government)
        *   [View all industries](https://github.com/solutions/industry)
        
    
    [View all solutions](https://github.com/solutions)
    
*   Resources
    
    *   EXPLORE BY TOPIC
        
        *   [AI](https://github.com/resources/articles?topic=ai)
        *   [Software Development](https://github.com/resources/articles?topic=software-development)
        *   [DevOps](https://github.com/resources/articles?topic=devops)
        *   [Security](https://github.com/resources/articles?topic=security)
        *   [View all topics](https://github.com/resources/articles)
        
    *   EXPLORE BY TYPE
        
        *   [Customer stories](https://github.com/customer-stories)
        *   [Events & webinars](https://github.com/resources/events)
        *   [Ebooks & reports](https://github.com/resources/whitepapers)
        *   [Business insights](https://github.com/solutions/executive-insights)
        *   [GitHub Skills](https://skills.github.com/)
        
    *   SUPPORT & SERVICES
        
        *   [Documentation](https://docs.github.com/)
        *   [Customer support](https://support.github.com/)
        *   [Community forum](https://github.com/orgs/community/discussions)
        *   [Trust center](https://github.com/trust-center)
        *   [Partners](https://github.com/partners)
        
    
    [View all resources](https://github.com/resources)
    
*   Open Source
    
    *   COMMUNITY
        
        *   [
            
            GitHub SponsorsFund open source developers
            
            ](https://github.com/sponsors)
        
    *   PROGRAMS
        
        *   [Security Lab](https://securitylab.github.com/)
        *   [Maintainer Community](https://maintainers.github.com/)
        *   [Accelerator](https://github.com/accelerator)
        *   [GitHub Stars](https://stars.github.com/)
        *   [Archive Program](https://archiveprogram.github.com/)
        
    *   REPOSITORIES
        
        *   [Topics](https://github.com/topics)
        *   [Trending](https://github.com/trending)
        *   [Collections](https://github.com/collections)
        
    
*   Enterprise
    
    *   ENTERPRISE SOLUTIONS
        
        *   [
            
            Enterprise platformAI-powered developer platform
            
            ](https://github.com/enterprise)
        
    *   AVAILABLE ADD-ONS
        
        *   [
            
            GitHub Advanced SecurityEnterprise-grade security features
            
            ](https://github.com/security/advanced-security)
        *   [
            
            Copilot for BusinessEnterprise-grade AI features
            
            ](https://github.com/features/copilot/copilot-business)
        *   [
            
            Premium SupportEnterprise-grade 24/7 support
            
            ](https://github.com/premium-support)
        
    
*   [Pricing](https://github.com/pricing)

Search or jump to...

# Search code, repositories, users, issues, pull requests...

Search

Clear

[Search syntax tips](https://docs.github.com/search-github/github-code-search/understanding-github-code-search-syntax)

# Provide feedback

We read every piece of feedback, and take your input very seriously.

Include my email address so I can be contacted

CancelSubmit feedback

# Saved searches

## Use saved searches to filter your results more quickly

Name

Query

To see all available qualifiers, see our[documentation](https://docs.github.com/search-github/github-code-search/understanding-github-code-search-syntax).

CancelCreate saved search

[Sign in](https://github.com/login?return_to=https%3A%2F%2Fgithub.com%2Fastral-sh%2Fuv%2Fissues%2F6867)

[Sign up](https://github.com/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F%3Cuser-name%3E%2F%3Crepo-name%3E%2Fvoltron%2Fissues_fragments%2Fissue_layout&source=header-repo&source_repo=astral-sh%2Fuv)

Appearance settings

Resetting focus

You signed in with another tab or window.[Reload](https://github.com/astral-sh/uv/issues/6867)to refresh your session.You signed out in another tab or window.[Reload](https://github.com/astral-sh/uv/issues/6867)to refresh your session.You switched accounts on another tab or window.[Reload](https://github.com/astral-sh/uv/issues/6867)to refresh your session.Dismiss alert

[astral-sh](https://github.com/astral-sh)/**[uv](https://github.com/astral-sh/uv)**Public

*   [Notifications](https://github.com/login?return_to=%2Fastral-sh%2Fuv)You must be signed in to change notification settings
*   [Fork3.1k](https://github.com/login?return_to=%2Fastral-sh%2Fuv)
*   [Star84.7k](https://github.com/login?return_to=%2Fastral-sh%2Fuv)
    

*   [Code](https://github.com/astral-sh/uv)
*   [Issues2.3k](https://github.com/astral-sh/uv/issues)
*   [Pull requests392](https://github.com/astral-sh/uv/pulls)
*   [Actions](https://github.com/astral-sh/uv/actions)
*   [Projects](https://github.com/astral-sh/uv/projects)
*   [Security and quality5](https://github.com/astral-sh/uv/security)
*   [Insights](https://github.com/astral-sh/uv/pulse)

Additional navigation options

*   [Code](https://github.com/astral-sh/uv)
*   [Issues](https://github.com/astral-sh/uv/issues)
*   [Pull requests](https://github.com/astral-sh/uv/pulls)
*   [Actions](https://github.com/astral-sh/uv/actions)
*   [Projects](https://github.com/astral-sh/uv/projects)
*   [Security and quality](https://github.com/astral-sh/uv/security)
*   [Insights](https://github.com/astral-sh/uv/pulse)

# Dockerfile with a workspace project#6867

[New issue](https://github.com/login?return_to=https://github.com/astral-sh/uv/issues/6867)

Copy link

[New issue](https://github.com/login?return_to=https://github.com/astral-sh/uv/issues/6867)

Copy link

Closed

Closed

[Dockerfile with a workspace project](https://github.com/astral-sh/uv/issues/6867#top)#6867

Copy link

Labels

[questionAsking for clarification or support](https://github.com/astral-sh/uv/issues?q=state%3Aopen%20label%3A%22question%22)Asking for clarification or support

[![@Afoucaul](https://avatars.githubusercontent.com/u/10498784?u=df6ddbd285eeee1e5749dcfe0bf6560ecfff478a&v=4&size=80)](https://github.com/Afoucaul)

## Description

[![@Afoucaul](https://avatars.githubusercontent.com/u/10498784?u=df6ddbd285eeee1e5749dcfe0bf6560ecfff478a&v=4&size=48)](https://github.com/Afoucaul)

[Afoucaul](https://github.com/Afoucaul)

opened[onAug 30, 2024](https://github.com/astral-sh/uv/issues/6867#issue-2497212276)·edited by[Afoucaul](https://github.com/Afoucaul)

Edits

Issue body actions

The[doc](https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers)proposes the following Dockerfile to build a project into a Dockerfile while caching intermediate layers (uv version 0.4.0):

```
#Install uvFROMpython:3.12-slimCOPY\--from=ghcr.io/astral-sh/uv:latest /uv /bin/uv#Change the working directory to the \`app\` directoryWORKDIR/app#Copy the lockfile and \`pyproject.toml\` into the imageADDuv.lock /app/uv.lockADDpyproject.toml /app/pyproject.toml#Install dependenciesRUNuv sync --frozen --no-install-project#Copy the project into the imageADD. /app#Sync the projectRUNuv sync --frozen
```

However, when the project is a worskpace,`uv sync --frozen --no-install-project`won't do anything unless the workspace members are there. As a result, if a workspace contains libs in a`libs/`dir, one has to also`ADD`all`libs/*/pyproject.toml`files so`uv sync --frozen --no-install-project`actually installs 3rd party dependencies.  
We could easily`COPY`the whole`libs/`dir, but then the cache would be invalidated every time sources change.

Is there a workaround? Or a workspace-specific strategy for building Docker images?

👀React with 👀1ThomAub

## Activity

[![charliermarsh](https://avatars.githubusercontent.com/u/1309177?u=6328c998d93a48eba87c6b039783b8a7644c62c3&v=4&size=80)](https://github.com/charliermarsh)

### charliermarsh commentedon Sep 1, 2024

[![@charliermarsh](https://avatars.githubusercontent.com/u/1309177?u=6328c998d93a48eba87c6b039783b8a7644c62c3&v=4&size=48)](https://github.com/charliermarsh)

[charliermarsh](https://github.com/charliermarsh)

[on Sep 1, 2024](https://github.com/astral-sh/uv/issues/6867#issuecomment-2323439037)

Member

More actions

Have you seen`uv sync --frozen --no-install-workspace`? That should omit the library and workspace members (but install all dependencies).

❤️React with ❤️1mserek

[![](https://avatars.githubusercontent.com/u/1309177?s=64&u=6328c998d93a48eba87c6b039783b8a7644c62c3&v=4)charliermarsh](https://github.com/charliermarsh)

added

[questionAsking for clarification or support](https://github.com/astral-sh/uv/issues?q=state%3Aopen%20label%3A%22question%22)Asking for clarification or support

[on Sep 1, 2024](https://github.com/astral-sh/uv/issues/6867#event-14095266082)

[![Afoucaul](https://avatars.githubusercontent.com/u/10498784?u=df6ddbd285eeee1e5749dcfe0bf6560ecfff478a&v=4&size=80)](https://github.com/Afoucaul)

### Afoucaul commentedon Sep 2, 2024

[![@Afoucaul](https://avatars.githubusercontent.com/u/10498784?u=df6ddbd285eeee1e5749dcfe0bf6560ecfff478a&v=4&size=48)](https://github.com/Afoucaul)

[Afoucaul](https://github.com/Afoucaul)

[on Sep 2, 2024](https://github.com/astral-sh/uv/issues/6867#issuecomment-2324087574)·edited by[Afoucaul](https://github.com/Afoucaul)

Edits

Author

More actions

> Have you seen`uv sync --frozen --no-install-workspace`? That should omit the library and workspace members (but install all dependencies).

Actually I have, and I may be failing to understand what`--frozen`does.  
When I run`uv sync --frozen --no-install-workspace`, nothing gets installed:

```
$ uv sync --frozen --no-install-workspace
Using Python 3.8.12
Creating virtualenv at: .venv
Auditedin0.00ms

$ ls -a .venv/lib/python3.8/site-packages 
\_virtualenv.pth \_virtualenv.py
```

However when I replace`--frozen`with`--locked`, packages do get installed, except indeed workspace members:

```
$ uv sync --locked --no-install-workspace
Resolved 16 packagesin2ms
Prepared 12 packagesin0.79ms
Installed 12 packagesin19ms
 + anyio==4.4.0
 + certifi==2024.8.30
 + charset-normalizer==3.3.2
 + exceptiongroup==1.2.2
 + h11==0.14.0
 + httpcore==1.0.5
 + httpx==0.27.2
 + idna==3.8
 + requests==2.32.3
 + sniffio==1.3.1
 + typing-extensions==4.12.2
 + urllib3==2.2.2

$ ls -a .venv/lib/python3.8/site-packages 
\_virtualenv.pth certifi-2024.8.30.dist-info h11 httpx-0.27.2.dist-info sniffio urllib3-2.2.2.dist-info
\_virtualenv.py charset\_normalizer h11-0.14.0.dist-info idna sniffio-1.3.1.dist-info 
anyio charset\_normalizer-3.3.2.dist-info httpcore idna-3.8.dist-info typing\_extensions-4.12.2.dist-info 
anyio-4.4.0.dist-info exceptiongroup httpcore-1.0.5.dist-info requests typing\_extensions.py 
certifi exceptiongroup-1.2.2.dist-info httpx requests-2.32.3.dist-info urllib3
```

From what I understand from`uv sync --help`,`--frozen`and`--locked`enforce the same behavior, except that`--locked`causes a failure if the lock file needs to be updated, while`--frozen`will proceed anyway:

```
\--locked Assert that the\`uv.lock\`will remain unchanged
 --frozen Sync without updating the\`uv.lock\`file
```

On that note, why would`--frozen`be recommended rather than`--locked`in Dockerfiles? It looks to me one would want to enforce as many static guarantees as possible at build time - but again I may be misunderstanding the purpose of these flags.

Am I missing something here? (I'm sorry the discussion is drifting a bit, I guess I'm confused with the`sync`command in general)

[![Afoucaul](https://avatars.githubusercontent.com/u/10498784?u=df6ddbd285eeee1e5749dcfe0bf6560ecfff478a&v=4&size=80)](https://github.com/Afoucaul)

### Afoucaul commentedon Sep 2, 2024

[![@Afoucaul](https://avatars.githubusercontent.com/u/10498784?u=df6ddbd285eeee1e5749dcfe0bf6560ecfff478a&v=4&size=48)](https://github.com/Afoucaul)

[Afoucaul](https://github.com/Afoucaul)

[on Sep 2, 2024](https://github.com/astral-sh/uv/issues/6867#issuecomment-2324132863)·edited by[Afoucaul](https://github.com/Afoucaul)

Edits

Author

More actions

I can confirm that with uv 0.4.0, and the following layout,`uv sync --frozen --no-install-workspace`does not install anything if I don't`ADD`the`pyproject.toml`file of apps and libs in the Dockerfile

Structure

```
.├── Dockerfile
├── README.md
├── apps
│ ├── app1
│ │ ├── README.md
│ │ ├── pyproject.toml
│ │ └── src
│ │ └── app1
│ │ └── \_\_init\_\_.py
│ └── app2
│ ├── README.md
│ ├── pyproject.toml
│ └── src
│ └── app2
│ └── \_\_init\_\_.py
├── libs
│ ├── lib1
│ │ ├── README.md
│ │ ├── pyproject.toml
│ │ └── src
│ │ └── lib1
│ │ └── \_\_init\_\_.py
│ └── lib2
│ ├── README.md
│ ├── pyproject.toml
│ └── src
│ └── lib2
│ └── \_\_init\_\_.py
├── pyproject.toml
├── src
│ └── uv\_monorepo\_test
│ └── \_\_init\_\_.py
└── uv.lock
```

## With child`pyproject.toml`files

```
#Install uvFROMpython:3.12-slimCOPY\--from=ghcr.io/astral-sh/uv:latest /uv /bin/uv#Change the working directory to the \`app\` directoryWORKDIR/app#Copy the lockfile and \`pyproject.toml\` into the imageADDuv.lock /app/uv.lockADDpyproject.toml /app/pyproject.toml#Add child pyproject.toml filesADDlibs/lib1/pyproject.toml /app/libs/lib1/pyproject.tomlADDlibs/lib2/pyproject.toml /app/libs/lib2/pyproject.tomlADDapps/app1/pyproject.toml /app/apps/app1/pyproject.tomlADDapps/app2/pyproject.toml /app/apps/app2/pyproject.toml#Install dependencies#Omitting --frozen because I don't understand how it behavesRUNuv sync --no-install-workspace
```

```
$ docker build --quiet.\-t demo&&docker run --rm demo ls -a .venv/lib/python3.12/site-packages
sha256:62dffa4e4e3d9d54af08c172042e1f3f84749fdc0fef56b6aa891407ae04eb44...
\_virtualenv.pth
\_virtualenv.py
anyio
anyio-4.4.0.dist-info
certifi
certifi-2024.8.30.dist-info
charset\_normalizer
charset\_normalizer-3.3.2.dist-info
charset\_normalizer.libs
h11
h11-0.14.0.dist-info
httpcore
httpcore-1.0.5.dist-info
httpx
httpx-0.27.2.dist-info
idna
idna-3.8.dist-info
requests
requests-2.32.3.dist-info
sniffio
sniffio-1.3.1.dist-info
urllib3
urllib3-2.2.2.dist-info
```

## Without child`pyproject.toml`files

```
#Install uvFROMpython:3.12-slimCOPY\--from=ghcr.io/astral-sh/uv:latest /uv /bin/uv#Change the working directory to the \`app\` directoryWORKDIR/app#Copy the lockfile and \`pyproject.toml\` into the imageADDuv.lock /app/uv.lockADDpyproject.toml /app/pyproject.toml#Add child pyproject.toml files#ADD libs/lib1/pyproject.toml /app/libs/lib1/pyproject.toml#ADD libs/lib2/pyproject.toml /app/libs/lib2/pyproject.toml#ADD apps/app1/pyproject.toml /app/apps/app1/pyproject.toml#ADD apps/app2/pyproject.toml /app/apps/app2/pyproject.toml#Install dependencies#Omitting --frozen because I don't understand how it behavesRUNuv sync --no-install-workspace
```

```
$ docker build --quiet.\-t demo&&docker run --rm demo ls -a .venv/lib/python3.12/site-packages
sha256:26cc1ba1a021cdc10d60c60f3015a545579a7a66f516dd81bb37ad1c60718c29...
\_virtualenv.pth
\_virtualenv.py
```

I'd be ok with`ADD`ing all`pyproject.toml`files, but Dockerfile`ADD`doesn't support a structure-preserving glob (eg an`ADD */*/pyproject.toml`that would add all`pyproject.toml`files under`apps/`or`libs/`, and which would end up at the same location in the Docker image), and`ADD`ing each file individually is tedious and error prone...

[![](https://avatars.githubusercontent.com/u/19817302?s=64&u=7496c641203d55b2450dffbb67661371ce61bfc1&v=4)carderne](https://github.com/carderne)

mentioned this[on Sep 2, 2024](https://github.com/astral-sh/uv/issues/6867#event-1422775865)

*   [Workspaces and monorepo support (add sync --all-packages)#6935](https://github.com/astral-sh/uv/issues/6935)
    

[![Afoucaul](https://avatars.githubusercontent.com/u/10498784?u=df6ddbd285eeee1e5749dcfe0bf6560ecfff478a&v=4&size=80)](https://github.com/Afoucaul)

### Afoucaul commentedon Sep 2, 2024

[![@Afoucaul](https://avatars.githubusercontent.com/u/10498784?u=df6ddbd285eeee1e5749dcfe0bf6560ecfff478a&v=4&size=48)](https://github.com/Afoucaul)

[Afoucaul](https://github.com/Afoucaul)

[on Sep 2, 2024](https://github.com/astral-sh/uv/issues/6867#issuecomment-2324793884)

Author

More actions

Closing in favor of[#6935](https://github.com/astral-sh/uv/issues/6935)

[![](https://avatars.githubusercontent.com/u/10498784?s=64&u=df6ddbd285eeee1e5749dcfe0bf6560ecfff478a&v=4)Afoucaul](https://github.com/Afoucaul)

closed this as[completed](https://github.com/astral-sh/uv/issues?q=is%3Aissue%20state%3Aclosed%20archived%3Afalse%20reason%3Acompleted)[on Sep 2, 2024](https://github.com/astral-sh/uv/issues/6867#event-14103889010)

[![](https://avatars.githubusercontent.com/in/347564?s=64&v=4)coderabbitai](https://github.com/apps/coderabbitai)

mentioned this[on Aug 3, 2025](https://github.com/astral-sh/uv/issues/6867#event-2891061542)

*   [Move to uvbgreenawald/bananagrams#75](https://github.com/bgreenawald/bananagrams/pull/75)
    

[Sign up for free](https://github.com/signup?return_to=https://github.com/astral-sh/uv/issues/6867)**to join this conversation on GitHub.**Already have an account?[Sign in to comment](https://github.com/login?return_to=https://github.com/astral-sh/uv/issues/6867)

## Metadata

## Metadata

### Assignees

No one assigned

### Labels

[questionAsking for clarification or support](https://github.com/astral-sh/uv/issues?q=state%3Aopen%20label%3A%22question%22)Asking for clarification or support

### Type

No type

### Projects

No projects

### Milestone

No milestone

### Relationships

None yet

### Development

No branches or pull requests

### Participants

[![@charliermarsh](https://avatars.githubusercontent.com/u/1309177?s=64&u=6328c998d93a48eba87c6b039783b8a7644c62c3&v=4)](https://github.com/charliermarsh)[![@Afoucaul](https://avatars.githubusercontent.com/u/10498784?s=64&u=df6ddbd285eeee1e5749dcfe0bf6560ecfff478a&v=4)](https://github.com/Afoucaul)

## Issue actions

## Footer

[](https://github.com/)© 2026 GitHub, Inc.

### Footer navigation

*   [Terms](https://docs.github.com/site-policy/github-terms/github-terms-of-service)
*   [Privacy](https://docs.github.com/site-policy/privacy-policies/github-privacy-statement)
*   [Security](https://github.com/security)
*   [Status](https://www.githubstatus.com/)
*   [Community](https://github.community/)
*   [Docs](https://docs.github.com/)
*   [Contact](https://support.github.com/?tags=dotcom-footer)
*   Manage cookies
*   Do not share my personal information

You can’t perform that action at this time.

Human readable version: https://github.com/astral-sh/uv/issues/6867