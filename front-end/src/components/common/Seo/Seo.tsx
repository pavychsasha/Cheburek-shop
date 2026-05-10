import {useEffect} from "react";

interface SeoProps {
    title: string;
    description: string;
    canonicalPath?: string;
    noindex?: boolean;
    jsonLd?: Record<string, unknown>;
}

const upsertMeta = (
    attributeName: "name" | "property",
    attributeValue: string,
    content: string,
) => {
    let element = document.head.querySelector<HTMLMetaElement>(
        `meta[${attributeName}="${attributeValue}"]`,
    );
    if (!element) {
        element = document.createElement("meta");
        element.setAttribute(attributeName, attributeValue);
        document.head.appendChild(element);
    }
    element.content = content;
};

const upsertCanonical = (href: string) => {
    let element = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]');
    if (!element) {
        element = document.createElement("link");
        element.rel = "canonical";
        document.head.appendChild(element);
    }
    element.href = href;
};

const Seo = ({
    title,
    description,
    canonicalPath = "/",
    noindex = false,
    jsonLd,
}: SeoProps) => {
    useEffect(() => {
        document.title = title;
        upsertMeta("name", "description", description);
        upsertMeta("name", "robots", noindex ? "noindex,nofollow" : "index,follow");
        upsertMeta("property", "og:title", title);
        upsertMeta("property", "og:description", description);
        upsertMeta("property", "og:type", "website");
        upsertMeta("name", "twitter:card", "summary_large_image");
        upsertMeta("name", "twitter:title", title);
        upsertMeta("name", "twitter:description", description);

        const canonicalUrl = new URL(canonicalPath, window.location.origin);
        upsertCanonical(canonicalUrl.href);

        const existingJsonLd = document.getElementById("app-json-ld");
        existingJsonLd?.remove();
        if (jsonLd) {
            const script = document.createElement("script");
            script.id = "app-json-ld";
            script.type = "application/ld+json";
            script.text = JSON.stringify(jsonLd);
            document.head.appendChild(script);
        }
    }, [canonicalPath, description, jsonLd, noindex, title]);

    return null;
};

export default Seo;
