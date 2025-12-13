# Rename titles in Paperless NGX using OpenAI

This is a Paperless NGX post consumption script.More information under this link : https://docs.paperless-ngx.com/advanced_usage/#consume-hooks.
You need an OpenAI API account to run it.

## Installation in Paperless NGX

We provide **two installation methods** - choose the one that fits your needs:

1. **Auto-Init Method** (Recommended) - Fully automated, no manual setup
2. **Standalone Single-File** (Simplest) - Ultra-minimal, one file only

---

### Method 1: Auto-Init Installation (Recommended)

This method automatically sets up the Python environment on container start. **No manual commands needed!**

#### Step 1: Copy ngx-renamer to your Paperless directory

```bash
cd ~/paperless  # or wherever your docker-compose.yml is located
git clone <repository-url> ngx-renamer
```

Your directory structure will look like:
```
~/paperless/
├── docker-compose.yml
├── docker-compose.env
├── consume/
├── export/
└── ngx-renamer/        # ← The cloned directory
    ├── change_title.py
    ├── modules/
    ├── scripts/        # ← New helper scripts
    ├── settings.yaml
    └── ...
```

#### Step 2: Configure API credentials

**Option A: Using .env file** (traditional method)
```bash
cd ngx-renamer
cp .env.example .env
nano .env  # Edit with your API keys
```

**Option B: Using docker-compose environment** (recommended for new installations)

Add to your `docker-compose.env` file:
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
PAPERLESS_NGX_API_KEY=your-paperless-api-token-here
PAPERLESS_NGX_URL=http://webserver:8000
```

> **Note:** Get your OpenAI API key from https://platform.openai.com/settings/organization/api-keys
>
> Get your Paperless API token from your Paperless user profile.

#### Step 3: Update docker-compose.yml

Add the following to your `webserver` service:

```yaml
webserver:
  image: ghcr.io/paperless-ngx/paperless-ngx:latest
  restart: unless-stopped
  depends_on:
    - db
    - broker
  ports:
    - "8000:8000"
  volumes:
    # Your existing volumes...
    - ./data:/usr/src/paperless/data
    - ./media:/usr/src/paperless/media
    - ./export:/usr/src/paperless/export
    - ./consume:/usr/src/paperless/consume

    # Add these two lines for ngx-renamer:
    - ./ngx-renamer:/usr/src/ngx-renamer:ro  # Source code (read-only)
    - ngx-renamer-venv:/usr/src/ngx-renamer-venv  # Persistent venv

  env_file: docker-compose.env
  environment:
    PAPERLESS_REDIS: redis://broker:6379
    PAPERLESS_DBHOST: db

    # Add this line to enable ngx-renamer:
    PAPERLESS_POST_CONSUME_SCRIPT: /usr/src/ngx-renamer/scripts/post_consume_wrapper.sh

  # Add this custom entrypoint:
  entrypoint: /usr/src/ngx-renamer/scripts/init-and-start.sh

# Add this at the bottom of your docker-compose.yml:
volumes:
  ngx-renamer-venv:  # Persistent volume for Python dependencies
```

#### Step 4: Restart Paperless

```bash
docker compose down
docker compose up -d
```

**That's it!** The first startup will take 30-60 seconds to initialize the Python environment. Subsequent restarts are instant.

Check the logs to verify:
```bash
docker compose logs webserver | grep ngx-renamer
```

You should see:
```
[ngx-renamer] Initializing Python environment...
[ngx-renamer] Python environment setup complete!
[ngx-renamer] Starting Paperless NGX...
```

---

### Method 2: Standalone Single-File Installation

This is the **simplest possible** installation - just one Python file!

#### Step 1: Copy the standalone script

```bash
cd ~/paperless
wget https://raw.githubusercontent.com/<your-repo>/ngx-renamer/main/ngx-renamer-standalone.py
# Or: curl -O https://...
```

#### Step 2: Update docker-compose.yml

```yaml
webserver:
  image: ghcr.io/paperless-ngx/paperless-ngx:latest
  volumes:
    # Your existing volumes...

    # Add this single line:
    - ./ngx-renamer-standalone.py:/usr/local/bin/ngx-renamer.py:ro

  environment:
    # Add these environment variables:
    PAPERLESS_POST_CONSUME_SCRIPT: python3 /usr/local/bin/ngx-renamer.py
    OPENAI_API_KEY: ${OPENAI_API_KEY}
    PAPERLESS_NGX_URL: http://webserver:8000
    PAPERLESS_NGX_API_KEY: ${PAPERLESS_API_KEY}
    OPENAI_MODEL: gpt-4o  # Optional: defaults to gpt-4o-mini
```

#### Step 3: Add credentials to .env

Create or edit your `.env` file in the same directory as `docker-compose.yml`:
```bash
OPENAI_API_KEY=sk-your-key-here
PAPERLESS_API_KEY=your-paperless-token-here
```

#### Step 4: Restart

```bash
docker compose down
docker compose up -d
```

**Done!** No setup, no venv, just one file.

---

### Migration from Old Installation Method

If you previously installed ngx-renamer using the manual `setup_venv.sh` method:

1. **Backup your `.env` file** (if using Method 1) or note your API keys
2. Follow the new installation instructions above
3. Remove the old manual setup:
   ```bash
   rm -rf ngx-renamer/venv  # Old venv no longer needed
   ```
4. The new method uses `/usr/src/ngx-renamer-venv` in a Docker volume instead

Your settings.yaml and configuration will continue to work as-is.

---

### Troubleshooting

#### Issue: "Python environment setup failed"

- **Check logs:** `docker compose logs webserver | grep ngx-renamer`
- **Verify volume:** `docker volume ls | grep ngx-renamer`
- **Manual setup:** `docker compose exec webserver /usr/src/ngx-renamer/scripts/setup-venv-if-needed.sh`

#### Issue: "Failed to get document details" or "Failed to update title"

- **Verify PAPERLESS_NGX_URL:** Must be accessible from inside the container
  - Use `http://webserver:8000` (service name), NOT `http://localhost:8000`
- **Check API key:** Verify your Paperless API token is correct
- **Test connectivity:** `docker compose exec webserver curl http://webserver:8000/api/`

#### Issue: "OPENAI_API_KEY environment variable not set"

- **Method 1 users:** Verify `.env` file exists in `ngx-renamer/` directory
- **Method 2 users:** Check environment variables in `docker-compose.yml`
- **Verify:** `docker compose exec webserver env | grep OPENAI`

#### Issue: Title generation not running after document upload

- **Check post-consume script is set:**
  ```bash
  docker compose exec webserver env | grep PAPERLESS_POST_CONSUME_SCRIPT
  ```
- **Manually trigger:** Upload a test document and check logs
- **Verify script is executable:**
  ```bash
  docker compose exec webserver ls -la /usr/src/ngx-renamer/scripts/
  ```

#### Issue: Dependencies changed but not updating

Method 1 auto-detects requirements.txt changes. To force rebuild:
```bash
docker compose exec webserver rm /usr/src/ngx-renamer-venv/.initialized
docker compose restart webserver
```

#### Issue: Want to update settings.yaml

Method 1: Just edit `settings.yaml` - **no restart needed!** Changes apply to next document.

Method 2: Edit environment variables in docker-compose.yml, then `docker compose up -d`

---

## The settings

You may edit `settings.yaml` to edit the prompt and with that the results.

**Test the different models at OpenAI:**
```yaml
openai_model: "gpt-4o-mini" # the model to use for the generation
```
**Decide whether you want to have a date as a prefix:**
```yaml
with_date: true # boolean if the title should the date as a prefix
```
**Play with the prompt - it is a work in progress and tested in Englsh and German:**
```yaml
prompt:
  # the main prompt for the AI
  main: |
    * this is a text from a PDF document generated with OCR
    * begin the text with the following line: ### begin of text ###
    * end the text with the following line: ### end of text ###
    * generate a title for that given text in the corresponding language
    * add the sender or author of the document with a maximum of 20 characters to the  title 
    * remove all stop words from the title
    * the  title must be in a Concise and Informative style
    * remove duplicate information
    * the length must be smaller that 200 characters
    * do not use asterisks in the title
    * do not use currencies in the result
    * optimize it for readability
    * check the result for filename conventions
    * re-read the generated  title and optimize it
  # the prompt part will be appended if the date should be included in the title using with_date: true
  with_date: |
    * analyze the text and find the date of the document
    * add the found date in form YYYY-MM-DD as a prefix to the doument title
    * if there is no date information in the document, use {current_date}
    * use the form: date sender title
  # the prompt part will be appended if the date should not be included in the title using with_date: false
  no_date: |
    * use the form: sender title
  # the prompt before the content of the document will be appended
  pre_content: |
    ### begin of text ###
  # the prompt after the content of the document will be appended
  post_content: |  
    ### end of text ###
```

## Python development and testing

If you want to develop and test is without integrating it in Paperless NGX you can do that.

* Create a virtual environment
* Load all libraries
* Call test scripts
* Enjoy optimizing the prompt in settings.yaml

### Create virtual environment

```bash
# python or python3 is up to your system
$ python3 -m venv .venv
$ source .venv/bin/activate
```

### Load all needed libraries

```bash
(.venv)$ pip install -r requirements.txt
```

### Call test scripts

```bash
# prints the thought title from a american law text
(.venv)$ python3 test_title.py
````

```bash
# read the content from a OCR'ed pdf file
(.venv)$ python3 ./test_pdf.py path/to/your/ocr-ed/pdf/file
