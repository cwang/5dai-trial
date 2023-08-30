<div id="top"></div>

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li>
          <a href="#scope">Scope</a>
        </li>
        <li>
          <a href="#assumptions">Assumptions</a>
        </li>
        <li>
          <a href="#design-decisions">Design Decisions</a>
        </li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#deployment">Deployment</a></li>
        <li><a href="#quick-run-through">Quick Run Through</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

A trial project for 5D AI.

It simulates a chat API layer using supplied documents.

### Scope

- Only an API layer and services backing it, no UI/UX.
- As an API client,
  - One can start a new task which is the equivalent of send first email to start an email thread per demo, optionally with documents
  - One can also continue the conversation in a task by asking more questions, which is the equivalent of sending following emails to an existing email thread, optionally with more documents
  - One can query any given task about existing conversations and documents attached
- As the system,
  - It offers the set of APIs (as described above) implemented by following [RAG](https://eugeneyan.com/writing/llm-patterns/#retrieval-augmented-generation-to-add-knowledge) pattern with the use of LLMs
  - It does not attempt to communicate out via any channels such as email, seeing it purely within any API client's responsibilities

### Assumptions

- No external integrations required such as Zapier
- Use of LLMs is via API calls to 3rd-party services such as OpenAI
- Ease of deployment is considered, supporting both direct and Docker-based deployments

### Design Decisions

In short, as a MVP (and a trial project), priority is given to implement a number of features over design a production-ready system.

It is a self-contained app that one can run locally and interact with to demonstrate its capabilities.

- Use local disk to store data, avoiding introducing dependencies such as a relational database and another vector database.
- Use OpenAI GPT-3.5-turbo with OpenAI embeddings, for the pairing is a tried and tested solution.
- No tests (as of now), QA done by manual testing.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

To run this project locally, you will need to install the prerequisites and follow the installation section.

### Prerequisites

This Project depends on the following projects.

- Poetry

  ```sh
  pip install --user --upgrade poetry
  ```

- Poe the Poet
  ```sh
  pip install --user --upgrade poethepoet
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/cwang/5dai-trial
   cd 5dai-trial
   ```
2. Install Poe the Poet and Poetry
   ```sh
   pip install --user --upgrade poethepoet poetry
   ```
3. Install requirements for development
   ```sh
   poe install-dev
   ```
4. Run tests
   ```sh
   poe test
   ```

### Deployment

It's automatically deployed to [Render](render.com) at

`https://fivedai-trial.onrender.com`

Replace the localhost url below with the Render url above to try it without running it locally.

### Quick Run Through

1. Run it locally (at port 8000)

```sh
poe uvicorn
```

2. Create first task (e.g. email thread) while uploading some PDFs at the same time

   ```sh
   curl -v http://127.0.0.1:8000/tasks -F 'question=Give me a list of the new technologies mentioned in the docs?' -F 'files=@misc/tr_technology_radar_vol_2_en.pdf'  -F 'files=@misc/tr_technology_radar_vol_1_en.pdf'
   ```

3. Capture the `id` of the task from the response; Wait 10-20 seconds and then read back the newly created task

   ```sh
   curl -v http://127.0.0.1:8000/tasks/1
   # Optionally pipe it to jq for better JSON readability
   ```

4. Continue with the task by asking another question

   ```sh
   curl -v http://127.0.0.1:8000/tasks/1 -F 'question=Which technologies in the list has been mention in both docs?'
   ```

5. Repeat step 3 to get latest answer as part of the response

6. More documents can be uploaded during the conversation with an existing task, such as

   ```sh
   curl -v http://127.0.0.1:8000/tasks/1 -F 'question=Which technologies are mentioned in all docs?' -F 'files=@misc/tr_technology_radar_vol_8_en.pdf'
   ```

7. More tasks can be created, as per step 2

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

Some useful examples of how this project can be used:

- Install requirements

  ```sh
  poe install-dev
  ```

- Run tests

  ```sh
  poe test
  ```

- Run the project via the main entrypoint

  ```sh
  poe run
  ```

- Generate API documentation

  ```sh
  poe doc
  ```

- Build a docker image for tests

  ```sh
  poe docker-build --target test --build-tag 3.10-alpine
  docker run -ti --rm 5dai:test-3.10-alpine
  ```

- Build a docker image to run the root files only without running any test

  ```sh
  poe docker-build --target prod --build-tag 3.10-alpine --no-test
  docker run -ti --rm 5dai:prod-3.10-alpine
  ```

- Lastly, run the project with Uvicorn with reloading enabled, running on port 8000 by default

  ```sh
  poe uvicorn
  ```

_For more examples, please refer to the [Documentation](https://cwang.github.io/5dai-trial/readme.html)_

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ROADMAP -->

## Roadmap

- [x] Add tests
- [x] Add code coverage
- [x] Improve documentation
- [ ] Include more tests

See the [open issues](https://github.com/cwang/fastapi-poetry-starter/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

Chen Wang - [@cwang](https://github.com/cwang) - dev@chenwang.org

Project Link: [https://github.com/cwang/5dai-trial/](https://github.com/cwang/5dai-trial/)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

This project was created using cookiecutter and NullHack's python-project-template:

- [NullHack's python-project-template](https://github.com/nullhack/python-project-template/)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the MIT License. See [`LICENSE`](https://github.com/cwang/fastapi-poetry-starter/blob/main/LICENSE) for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/cwang/fastapi-poetry-starter.svg?style=for-the-badge
[contributors-url]: https://github.com/cwang/fastapi-poetry-starter/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/cwang/fastapi-poetry-starter.svg?style=for-the-badge
[forks-url]: https://github.com/cwang/fastapi-poetry-starter/network/members
[stars-shield]: https://img.shields.io/github/stars/cwang/fastapi-poetry-starter.svg?style=for-the-badge
[stars-url]: https://github.com/cwang/fastapi-poetry-starter/stargazers
[issues-shield]: https://img.shields.io/github/issues/cwang/fastapi-poetry-starter.svg?style=for-the-badge
[issues-url]: https://github.com/cwang/fastapi-poetry-starter/issues
[license-shield]: https://img.shields.io/badge/license-MIT-green?style=for-the-badge
[license-url]: https://github.com/cwang/fastapi-poetry-starter/blob/main/LICENSE
