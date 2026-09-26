import { readFile, access } from "node:fs/promises";
import { join } from "node:path";

const root = new URL(".", import.meta.url).pathname;
const themes = [
  "market-grid",
  "property-editorial",
  "service-list",
  "tech-showcase",
];
const pages = ["index.html", "catalog.html", "show.html", "404.html"];
const requiredImage = {
  "market-grid": "images/catalog-atlas.png",
  "property-editorial": "images/catalog-atlas.png",
  "service-list": "images/catalog-atlas.png",
  "tech-showcase": "images/catalog-atlas.png",
};
const requiredClasses = [
  "site-header",
  "site-header__brand",
  "site-nav",
  "page__main",
  "site-footer",
];
const bemClassPattern =
  /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:__(?:[a-z][a-z0-9]*(?:-[a-z0-9]+)*))?(?:--(?:[a-z][a-z0-9]*(?:-[a-z0-9]+)*))?$/;
const requiredCssMarkerBlocks = [
  "Основа теми",
  "Блок notification-menu",
  "Блок partners",
];
const voidElements = new Set([
  "area",
  "base",
  "br",
  "col",
  "embed",
  "hr",
  "img",
  "input",
  "link",
  "meta",
  "param",
  "source",
  "track",
  "wbr",
]);

function findDetachedBemElements(html) {
  const issues = [];
  const stack = [];
  const tags = html.matchAll(/<(\/?)([a-z][a-z0-9-]*)\b([^>]*)>/gi);

  for (const [, slash, rawTag, attributes] of tags) {
    const tag = rawTag.toLowerCase();
    if (slash) {
      const index = stack.findLastIndex((entry) => entry.tag === tag);
      if (index >= 0) stack.splice(index);
      continue;
    }

    const classMatch = attributes.match(/\bclass="([^"]+)"/);
    const classNames = classMatch ? classMatch[1].trim().split(/\s+/) : [];
    const availableClasses = new Set(classNames);
    for (const entry of stack) {
      for (const className of entry.classNames) {
        availableClasses.add(className);
      }
    }

    for (const className of classNames) {
      if (!className.includes("__")) continue;
      const block = className.split("__", 1)[0];
      if (!availableClasses.has(block)) issues.push(className);
    }

    if (!voidElements.has(tag) && !attributes.trimEnd().endsWith("/")) {
      stack.push({ tag, classNames });
    }
  }

  return issues;
}

let errors = [];

for (const theme of themes) {
  const directory = join(root, theme);
  for (const file of [
    ...pages,
    "styles.css",
    requiredImage[theme],
    "images/partner-logos.svg",
    "partners.js",
  ]) {
    try {
      await access(join(directory, file));
    } catch {
      errors.push(theme + ": відсутній " + file);
    }
  }

  for (const page of pages) {
    const html = await readFile(join(directory, page), "utf8");
    if (/<iframe\b/i.test(html)) {
      errors.push(theme + "/" + page + ": заборонений iframe");
    }
    const scripts = html.match(/<script\b[^>]*>.*?<\/script>/gis) ?? [];
    const allowedScript = '<script src="partners.js" defer></script>';
    if (scripts.some((script) => script.trim() !== allowedScript)) {
      errors.push(
        theme + "/" + page + ": знайдено сторонній або inline script",
      );
    }
    if (/(?:src|href)=["']https?:\/\//i.test(html)) {
      errors.push(theme + "/" + page + ": знайдено зовнішній ресурс");
    }
    for (const contractPart of [
      'class="notification-menu"',
      'data-component="notification-center"',
      'data-endpoint="/api/notifications"',
      "data-notification-list",
      'data-action="mark-read"',
      'data-action="mark-all-read"',
    ]) {
      if (!html.includes(contractPart)) {
        errors.push(
          theme + "/" + page + ": порушено контракт сповіщень " + contractPart,
        );
      }
    }

    for (const className of requiredClasses) {
      if (
        !html.includes('class="' + className) &&
        !html.includes(" " + className)
      ) {
        errors.push(theme + "/" + page + ": немає класу " + className);
      }
    }

    for (const className of findDetachedBemElements(html)) {
      errors.push(
        theme +
          "/" +
          page +
          ": BEM-елемент використано поза своїм блоком " +
          className,
      );
    }

    const classAttributes = [...html.matchAll(/\bclass="([^"]+)"/g)];
    for (const [, classValue] of classAttributes) {
      const classNames = classValue.trim().split(/\s+/);
      for (const className of classNames) {
        if (!bemClassPattern.test(className)) {
          errors.push(
            theme + "/" + page + ": клас не відповідає BEM " + className,
          );
        }
        if (className.includes("--")) {
          const baseClass = className.split("--", 1)[0];
          if (!classNames.includes(baseClass)) {
            errors.push(
              theme +
                "/" +
                page +
                ": модифікатор " +
                className +
                " використано без " +
                baseClass,
            );
          }
        }
      }
    }
  }

  const home = await readFile(join(directory, "index.html"), "utf8");
  if ((home.match(/class="catalog-card/g) ?? []).length < 3) {
    errors.push(
      theme + ": головна сторінка має показувати три рекомендовані позиції",
    );
  }
  for (const partnerPart of [
    'class="partners"',
    'class="partners__track"',
    "images/partner-logos.svg#logo-",
    "data-partners-slider",
    'data-action="partners-previous"',
    'data-action="partners-next"',
    'src="partners.js"',
  ]) {
    if (!home.includes(partnerPart)) {
      errors.push(
        theme +
          ": головна сторінка не містить слайдер партнерів " +
          partnerPart,
      );
    }
  }

  if (!home.includes('id="featured"')) {
    errors.push(
      theme + ": на головній сторінці немає акцентного блока featured",
    );
  }

  for (const operation of ["sale", "rent"]) {
    if (
      !home.includes('name="operation"') ||
      !home.includes('value="' + operation + '"')
    ) {
      errors.push(theme + ": форма пошуку не містить операцію " + operation);
    }
  }

  const show = await readFile(join(directory, "show.html"), "utf8");
  for (const requestPart of [
    'data-action="request"',
    'data-endpoint="/api/requests"',
    "data-item",
  ]) {
    if (!show.includes(requestPart)) {
      errors.push(theme + ": порушено контракт кнопки заявки " + requestPart);
    }
  }

  const catalog = await readFile(join(directory, "catalog.html"), "utf8");
  if ((catalog.match(/class="catalog-card/g) ?? []).length < 3) {
    errors.push(
      theme + ": каталог має показувати щонайменше три демонстраційні картки",
    );
  }

  const css = await readFile(join(directory, "styles.css"), "utf8");
  for (const selector of [
    ".catalog-card",
    ".catalog-card__title",
    ".catalog-card--featured",
  ]) {
    if (!css.includes(selector))
      errors.push(theme + ": у CSS немає " + selector);
  }
  if (!css.includes("@media"))
    errors.push(theme + ": немає адаптивного правила @media");
  for (const block of requiredCssMarkerBlocks) {
    for (const edge of ["початок", "кінець"]) {
      const marker = "/* === " + block + " · " + edge + " === */";
      if (!css.includes(marker)) {
        errors.push(theme + ": у CSS немає маркера " + marker);
      }
    }
  }
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}

console.log("OK: перевірено 4 теми, 16 HTML-сторінок і локальні ресурси.");
