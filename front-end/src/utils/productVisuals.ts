const categoryStyles: Record<string, {primary: string; accent: string; shape: string}> = {
    Chebureks: {
        primary: "#f4b14c",
        accent: "#b54f3e",
        shape: `<path d="M74 126c25-76 118-109 192-47 24 20 27 57 4 80-48 49-154 58-196-33Z" fill="PRIMARY" stroke="ACCENT" stroke-width="14" stroke-linejoin="round"/><path d="M94 122c49 19 123 20 174 0" fill="none" stroke="#fff5d7" stroke-width="10" stroke-linecap="round"/><path d="M129 95c25-22 54-34 88-38" fill="none" stroke="ACCENT" stroke-width="8" stroke-linecap="round" opacity=".52"/>`,
    },
    Pies: {
        primary: "#d9a65f",
        accent: "#7a583a",
        shape: `<ellipse cx="180" cy="132" rx="112" ry="58" fill="PRIMARY" stroke="ACCENT" stroke-width="13"/><path d="M88 126c42-28 123-34 181-9" fill="none" stroke="#fff4d2" stroke-width="10" stroke-linecap="round"/><path d="M130 95c12 18 15 38 8 58M182 87c9 25 8 51-3 73M235 98c-12 20-17 39-16 58" fill="none" stroke="ACCENT" stroke-width="7" stroke-linecap="round" opacity=".55"/>`,
    },
    Drinks: {
        primary: "#d95243",
        accent: "#2f7180",
        shape: `<rect x="112" y="52" width="55" height="154" rx="24" fill="PRIMARY" stroke="#8e392f" stroke-width="9"/><rect x="124" y="27" width="31" height="34" rx="10" fill="#7fc0cf" stroke="ACCENT" stroke-width="7"/><rect x="196" y="82" width="76" height="110" rx="20" fill="#fff7ef" stroke="PRIMARY" stroke-width="10"/><path d="M205 111h56M204 192h70" stroke="PRIMARY" stroke-width="8" stroke-linecap="round"/>`,
    },
    Other: {
        primary: "#f0cd71",
        accent: "#75533a",
        shape: `<rect x="83" y="82" width="177" height="104" rx="26" fill="PRIMARY" stroke="ACCENT" stroke-width="11"/><path d="M108 113h126M108 149h86" stroke="#fff8d9" stroke-width="12" stroke-linecap="round"/><circle cx="259" cy="193" r="33" fill="#7fc0cf" stroke="#2f7180" stroke-width="8"/>`,
    },
};

const defaultStyle = categoryStyles.Chebureks;

export const categoryFallbackSvg = (category?: string) => {
    const style = categoryStyles[category || ""] || defaultStyle;
    const shape = style.shape
        .replace(/PRIMARY/g, style.primary)
        .replace(/ACCENT/g, style.accent);
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="360" height="280" viewBox="0 0 360 280" role="img" aria-label="${category || "Product"} illustration"><rect width="360" height="280" rx="28" fill="#fff7ef"/><circle cx="287" cy="62" r="38" fill="${style.primary}" opacity=".18"/><circle cx="73" cy="214" r="50" fill="${style.accent}" opacity=".12"/><g transform="translate(0 24)">${shape}</g></svg>`;
    return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
};
