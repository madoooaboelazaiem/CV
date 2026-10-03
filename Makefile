# make build      build dist/ (main site + dist/editorial/)
# make serve      build and open http://localhost:8000  (add /#edit to the URL to edit content in the browser)
# make check      validate site/content.json, then warn about phone numbers in public files
# make qa         screenshot every section on desktop and mobile, report JS errors and overflow
# make showcase   regenerate the README GIF, screenshots and social-preview image (needs playwright + ffmpeg)
# make clean
PY       ?= python3
SITE_URL ?=
ROOT     := $(if $(SITE_URL),$(patsubst %/,%,$(SITE_URL))/)
CV       := $(wildcard assets/cv.pdf)
CARD     := $(wildcard assets/card.png)
COMMON    = --content site/content.json --photo assets/photo.png --avatar assets/avatar.png \
            $(if $(CARD),--card $(CARD)) $(if $(CV),--cv $(CV))

.PHONY: build serve check qa showcase clean

build:
	@mkdir -p dist/editorial
	$(PY) scripts/build.py $(COMMON) --theme sketch    --out dist/index.html \
	  $(if $(ROOT),--url $(ROOT) --og-image $(ROOT)social-preview.png)
	$(PY) scripts/build.py $(COMMON) --theme editorial --out dist/editorial/index.html \
	  $(if $(ROOT),--url $(ROOT)editorial/ --og-image $(ROOT)social-preview.png)
	@cp docs/img/social-preview.png dist/social-preview.png 2>/dev/null || echo "note: docs/img/social-preview.png missing (run make showcase)"

serve: build
	@echo "Open http://localhost:8000   (editor: http://localhost:8000/#edit)"
	$(PY) -m http.server 8000 -d dist

check:
	$(PY) scripts/validate_content.py
	$(PY) scripts/privacy_check.py

qa: build
	$(PY) scripts/qa.py dist/index.html dist-qa/sketch
	$(PY) scripts/qa.py dist/editorial/index.html dist-qa/editorial

showcase: build
	$(PY) scripts/capture_showcase.py --dist dist --out docs/img

clean:
	rm -rf dist dist-qa
