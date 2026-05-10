import {DragEvent, FormEvent, ReactNode, useCallback, useEffect, useMemo, useRef, useState} from "react";
import {
    Area,
    AreaChart,
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    Line,
    LineChart,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

import {
    ADMIN_TOKEN_KEY,
    backfillProductTranslations,
    clearAdminToken,
    createProduct,
    createUser,
    deleteOrder,
    deleteProduct,
    deleteUser,
    fetchAdminAnalytics,
    fetchAdminAnalyticsForWidget,
    fetchAdminMe,
    fetchAdminSummary,
    fetchDashboardPreferences,
    fetchOrders,
    fetchProduct,
    fetchProducts,
    fetchPublicSettings as fetchAdminPublicSettings,
    fetchUsers,
    getAdminErrorMessage,
    loginAdmin,
    previewProductTranslations,
    seedProducts,
    updateCurrencySettings,
    updateDashboardPreferences,
    updateOrderNotes,
    updateOrderStatus,
    updateProduct,
    updateProductLanguageSettings,
    updateProfitSettings,
    updateUserFlags,
    uploadProductImage,
} from "./api.ts";
import styles from "./AdminApp.module.scss";
import type {
    AdminAnalytics,
    AdminOrder,
    AdminProduct,
    AdminSummary,
    AdminUser,
    AdminView,
    CurrencySettingsUpdate,
    DashboardChartType,
    DashboardPreferences,
    DashboardWidgetPreference,
    OrderStatus,
    ProductFormState,
    ProductTranslation,
} from "./types.ts";
import {useCurrencyFormatter} from "../hooks/useCurrencyFormatter.ts";
import {useAppDispatch, useAppSelector} from "../redux/hooks.ts";
import {fetchPublicSettings as refreshPublicSettings} from "../redux/slices/settingsSlice.ts";
import {categoryFallbackSvg} from "../utils/productVisuals.ts";

const ORDER_STATUSES: OrderStatus[] = [
    "PENDING",
    "CONFIRMED",
    "PREPARING",
    "READY",
    "DELIVERED",
    "CANCELLED",
];

const DEFAULT_PRODUCT_LANGUAGES = ["en", "ukr"];

const normalizeLanguageCode = (value: string) =>
    value.trim().toLowerCase().replace(/[^a-z0-9-]/g, "");

const uniqueLanguageCodes = (languages: string[]) =>
    Array.from(
        new Set(
            languages
                .map(normalizeLanguageCode)
                .filter(Boolean),
        ),
    );

const languageLabel = (languageCode: string) => languageCode.toUpperCase();

const draftTranslation = (
    languageCode: string,
    source?: ProductTranslation,
): ProductTranslation => ({
    language_code: languageCode,
    product_name: source?.product_name
        ? `${source.product_name}${languageCode === "en" ? "" : ` (${languageLabel(languageCode)})`}`
        : "",
    product_description: source?.product_description || "",
});

const ensureProductTranslations = (
    languages: string[],
    translations: ProductTranslation[] = [],
): ProductTranslation[] => {
    const configuredLanguages = uniqueLanguageCodes(languages).length
        ? uniqueLanguageCodes(languages)
        : DEFAULT_PRODUCT_LANGUAGES;
    const normalizedTranslations = translations
        .map((translation) => ({
            ...translation,
            language_code: normalizeLanguageCode(translation.language_code),
        }))
        .filter((translation) => translation.language_code);
    const translationsByLanguage = new Map(
        normalizedTranslations.map((translation) => [
            translation.language_code,
            translation,
        ]),
    );
    const source =
        translationsByLanguage.get("en") ||
        normalizedTranslations[0] ||
        undefined;

    configuredLanguages.forEach((languageCode) => {
        if (!translationsByLanguage.has(languageCode)) {
            translationsByLanguage.set(languageCode, draftTranslation(languageCode, source));
        }
    });

    return configuredLanguages
        .map((languageCode) => translationsByLanguage.get(languageCode))
        .filter((translation): translation is ProductTranslation => Boolean(translation));
};

const emptyProductForm = (
    languages: string[] = DEFAULT_PRODUCT_LANGUAGES,
): ProductFormState => ({
    price: "",
    cost_price: "",
    category: "Chebureks",
    stock_quantity: "0",
    image_src: "",
    tags: "",
    translations: ensureProductTranslations(languages),
});

const productToForm = (
    product: AdminProduct,
    languages: string[] = DEFAULT_PRODUCT_LANGUAGES,
): ProductFormState => ({
    price: String(product.price),
    cost_price: String(product.cost_price || ""),
    category: product.category || "Chebureks",
    stock_quantity: String(product.stock_quantity),
    image_src: product.image_src,
    tags: product.tags?.join(", ") || "",
    translations: ensureProductTranslations(
        languages,
        product.translations?.length
            ? product.translations
            : [
                  {
                      language_code: "en",
                      product_name: product.name || "",
                      product_description: product.description || "",
                  },
              ],
    ),
});

const CHART_COLORS = ["#2f6f5e", "#c84f3f", "#f2ad4b", "#6b7280", "#5f6fb2", "#9a6438"];

const DEFAULT_DASHBOARD_WIDGETS: DashboardWidgetPreference[] = [
    {id: "metrics", visible: true, position: 0, timespan_days: 30, period: "day"},
    {id: "revenue", visible: true, chart_type: "line", position: 1, timespan_days: 30, period: "day"},
    {id: "profit", visible: true, chart_type: "area", position: 2, timespan_days: 30, period: "day"},
    {id: "orders", visible: true, chart_type: "bar", position: 3, timespan_days: 30, period: "day"},
    {id: "visitors", visible: true, chart_type: "area", position: 4, timespan_days: 30, period: "day"},
    {id: "status", visible: true, chart_type: "pie", position: 5, timespan_days: 30, period: "day"},
    {id: "top-products", visible: true, position: 6, timespan_days: 30, period: "day"},
    {id: "low-stock", visible: true, position: 7, timespan_days: 30, period: "day"},
    {id: "recent-orders", visible: true, position: 8, timespan_days: 30, period: "day"},
];

const DASHBOARD_WIDGET_LABELS: Record<string, string> = {
    metrics: "Metric cards",
    revenue: "Revenue over time",
    profit: "Profit over time",
    orders: "Orders by day",
    visitors: "Visitors and page views",
    status: "Order status mix",
    "top-products": "Top products",
    "low-stock": "Low stock",
    "recent-orders": "Recent orders",
};

const CHART_TYPES: DashboardChartType[] = ["line", "bar", "area", "pie"];

interface AdminSelectOption {
    value: string;
    label: string;
}

interface AdminSelectProps {
    value: string;
    options: AdminSelectOption[];
    ariaLabel: string;
    onChange: (value: string) => void;
    disabled?: boolean;
}

const AdminSelect = ({
    value,
    options,
    ariaLabel,
    onChange,
    disabled = false,
}: AdminSelectProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const selectRef = useRef<HTMLDivElement | null>(null);
    const selectedOption = options.find((option) => option.value === value) || options[0];

    useEffect(() => {
        if (!isOpen) {
            return;
        }

        const closeOnOutsideClick = (event: PointerEvent) => {
            if (
                selectRef.current &&
                !selectRef.current.contains(event.target as Node)
            ) {
                setIsOpen(false);
            }
        };

        document.addEventListener("pointerdown", closeOnOutsideClick);
        return () => document.removeEventListener("pointerdown", closeOnOutsideClick);
    }, [isOpen]);

    return (
        <div className={styles.adminSelect} ref={selectRef}>
            <button
                type="button"
                className={styles.adminSelectButton}
                aria-haspopup="listbox"
                aria-expanded={isOpen}
                aria-label={ariaLabel}
                disabled={disabled}
                onClick={() => setIsOpen((current) => !current)}
            >
                <span>{selectedOption?.label || "Select"}</span>
            </button>
            {isOpen && !disabled && (
                <div className={styles.adminSelectMenu} role="listbox" aria-label={ariaLabel}>
                    {options.map((option) => {
                        const isSelected = option.value === value;
                        return (
                            <button
                                key={option.value}
                                type="button"
                                role="option"
                                aria-selected={isSelected}
                                className={
                                    isSelected
                                        ? styles.adminSelectOptionSelected
                                        : styles.adminSelectOption
                                }
                                onClick={() => {
                                    onChange(option.value);
                                    setIsOpen(false);
                                }}
                            >
                                {option.label}
                            </button>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

const AdminApp = () => {
    const [authState, setAuthState] = useState<"loading" | "login" | "ready" | "forbidden">(
        "loading",
    );
    const [currentUser, setCurrentUser] = useState<AdminUser | null>(null);
    const [activeView, setActiveView] = useState<AdminView>("dashboard");

    const verifySession = useCallback(async () => {
        if (!sessionStorage.getItem(ADMIN_TOKEN_KEY)) {
            setAuthState("login");
            return;
        }

        try {
            const user = await fetchAdminMe();
            if (!user.is_superuser) {
                clearAdminToken();
                setAuthState("forbidden");
                return;
            }
            setCurrentUser(user);
            setAuthState("ready");
        } catch {
            setAuthState("login");
        }
    }, []);

    useEffect(() => {
        const timeoutId = window.setTimeout(() => {
            void verifySession();
        }, 0);
        return () => window.clearTimeout(timeoutId);
    }, [verifySession]);

    const handleLogin = (user: AdminUser) => {
        setCurrentUser(user);
        setAuthState("ready");
    };

    const handleLogout = () => {
        clearAdminToken();
        setCurrentUser(null);
        setAuthState("login");
    };

    if (authState === "loading") {
        return <AdminMessage title="Checking admin access" message="Preparing the back-office workspace." />;
    }

    if (authState === "login") {
        return <AdminLogin onLogin={handleLogin} />;
    }

    if (authState === "forbidden") {
        return (
            <AdminMessage
                title="Admin access required"
                message="The signed-in account is active, but it is not allowed to manage the shop."
                actionLabel="Return to login"
                onAction={() => setAuthState("login")}
            />
        );
    }

    return (
        <main className={styles.shell}>
            <aside className={styles.sidebar} aria-label="Admin navigation">
                <div>
                    <p className={styles.eyebrow}>Back office</p>
                    <h1>Cheburek Shop</h1>
                </div>
                <nav className={styles.nav}>
                    {(["dashboard", "products", "orders", "users", "settings"] as AdminView[]).map((view) => (
                        <button
                            key={view}
                            type="button"
                            className={activeView === view ? styles.navActive : ""}
                            onClick={() => setActiveView(view)}
                        >
                            {view}
                        </button>
                    ))}
                </nav>
                <div className={styles.account}>
                    <span>{currentUser?.email}</span>
                    <button type="button" onClick={handleLogout}>
                        Sign out
                    </button>
                </div>
            </aside>

            <section className={styles.workspace}>
                {activeView === "dashboard" && <DashboardPanel />}
                {activeView === "products" && <ProductsPanel />}
                {activeView === "orders" && <OrdersPanel />}
                {activeView === "users" && currentUser && <UsersPanel currentUser={currentUser} />}
                {activeView === "settings" && <SettingsPanel />}
            </section>
        </main>
    );
};

interface AdminMessageProps {
    title: string;
    message: string;
    actionLabel?: string;
    onAction?: () => void;
}

const AdminMessage = ({title, message, actionLabel, onAction}: AdminMessageProps) => (
    <main className={styles.authPage}>
        <section className={styles.authPanel}>
            <p className={styles.eyebrow}>Admin portal</p>
            <h1>{title}</h1>
            <p>{message}</p>
            {actionLabel && onAction && (
                <button type="button" className={styles.primaryButton} onClick={onAction}>
                    {actionLabel}
                </button>
            )}
        </section>
    </main>
);

const AdminLogin = ({onLogin}: {onLogin: (user: AdminUser) => void}) => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    const submitLogin = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError("");
        setIsSubmitting(true);

        try {
            const user = await loginAdmin(email, password);
            onLogin(user);
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to sign in."));
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <main className={styles.authPage}>
            <form className={styles.authPanel} onSubmit={submitLogin}>
                <p className={styles.eyebrow}>Admin portal</p>
                <h1>Back-office sign in</h1>
                <label>
                    Email
                    <input
                        type="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        required
                        autoComplete="username"
                    />
                </label>
                <label>
                    Password
                    <input
                        type="password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        required
                        minLength={8}
                        autoComplete="current-password"
                    />
                </label>
                {error && <p className={styles.error}>{error}</p>}
                <button type="submit" className={styles.primaryButton} disabled={isSubmitting}>
                    {isSubmitting ? "Signing in" : "Sign in"}
                </button>
            </form>
        </main>
    );
};

const DashboardPanel = () => {
    const [summary, setSummary] = useState<AdminSummary | null>(null);
    const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null);
    const [widgetAnalytics, setWidgetAnalytics] = useState<Record<string, AdminAnalytics>>({});
    const [preferences, setPreferences] = useState<DashboardPreferences>({
        widgets: DEFAULT_DASHBOARD_WIDGETS,
    });
    const [error, setError] = useState("");
    const [savingPreference, setSavingPreference] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const formatPrice = useCurrencyFormatter();

    const loadSummary = useCallback(async () => {
        setIsLoading(true);
        setError("");
        try {
            const [nextSummary, nextAnalytics, nextPreferences] = await Promise.all([
                fetchAdminSummary(),
                fetchAdminAnalytics(),
                fetchDashboardPreferences(),
            ]);
            setSummary(nextSummary);
            setAnalytics(nextAnalytics);
            setWidgetAnalytics({});
            setPreferences(nextPreferences);
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to load dashboard."));
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        const timeoutId = window.setTimeout(() => {
            void loadSummary();
        }, 0);
        return () => window.clearTimeout(timeoutId);
    }, [loadSummary]);

    const cards = summary
        ? [
              ["Products", summary.products_count],
              ["Orders", summary.orders_count],
              ["Users", summary.users_count],
              ["Low stock", summary.low_stock_products_count],
              ["Pending", summary.pending_orders_count],
              ["Visitors today", summary.unique_visitors_today],
              ["Page views today", summary.page_views_today],
              ["Revenue", formatPrice(summary.total_revenue)],
              ["Gross profit", formatPrice(summary.gross_profit)],
              ["Estimated profit", formatPrice(summary.estimated_profit)],
              ["Profit margin", `${summary.profit_margin_percent}%`],
              ["Avg. order", formatPrice(summary.average_order_value)],
          ]
        : [];

    const sortedWidgets = preferences.widgets
        .map((widget) => ({
            ...DEFAULT_DASHBOARD_WIDGETS.find((defaultWidget) => defaultWidget.id === widget.id),
            ...widget,
        }))
        .sort((left, right) => left.position - right.position);

    const persistPreferences = async (
        nextWidgets: DashboardWidgetPreference[],
        widgetId?: string,
    ) => {
        const nextPreferences = {
            widgets: nextWidgets.map((widget, index) => ({...widget, position: index})),
        };
        setPreferences(nextPreferences);
        setSavingPreference(widgetId || "dashboard");
        try {
            await updateDashboardPreferences(nextPreferences);
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to save dashboard preferences."));
        } finally {
            setSavingPreference("");
        }
    };

    const updateWidget = (
        widgetId: string,
        update: Partial<DashboardWidgetPreference>,
    ) => {
        const nextWidgets = sortedWidgets.map((widget) =>
            widget.id === widgetId ? {...widget, ...update} : widget,
        );
        void persistPreferences(nextWidgets, widgetId);
        const nextWidget = nextWidgets.find((widget) => widget.id === widgetId);
        if (nextWidget && ("timespan_days" in update || "period" in update)) {
            void fetchAdminAnalyticsForWidget(nextWidget.timespan_days, nextWidget.period)
                .then((nextAnalytics) =>
                    setWidgetAnalytics((current) => ({
                        ...current,
                        [widgetId]: nextAnalytics,
                    })),
                )
                .catch((requestError) =>
                    setError(
                        getAdminErrorMessage(
                            requestError,
                            "Unable to load widget analytics.",
                        ),
                    ),
                );
        }
    };

    const moveWidget = (widgetId: string, direction: -1 | 1) => {
        const currentIndex = sortedWidgets.findIndex((widget) => widget.id === widgetId);
        const nextIndex = currentIndex + direction;
        if (currentIndex < 0 || nextIndex < 0 || nextIndex >= sortedWidgets.length) {
            return;
        }
        const nextWidgets = [...sortedWidgets];
        const [widget] = nextWidgets.splice(currentIndex, 1);
        nextWidgets.splice(nextIndex, 0, widget);
        void persistPreferences(nextWidgets, widgetId);
    };

    const renderSeriesChart = (
        data: {date: string; value: number}[],
        chartType: DashboardChartType | null | undefined,
        color: string,
        formatter?: (value: number) => string,
    ) => {
        if (chartType === "pie") {
            return (
                <PieChart>
                    <Pie data={data} dataKey="value" nameKey="date" outerRadius={86} label>
                        {data.map((entry, index) => (
                            <Cell
                                key={`${entry.date}-${entry.value}`}
                                fill={CHART_COLORS[index % CHART_COLORS.length]}
                            />
                        ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatter ? formatter(Number(value)) : value} />
                </PieChart>
            );
        }
        if (chartType === "bar") {
            return (
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5ebe8" />
                    <XAxis dataKey="date" tick={{fontSize: 12}} />
                    <YAxis tick={{fontSize: 12}} />
                    <Tooltip formatter={(value) => formatter ? formatter(Number(value)) : value} />
                    <Bar dataKey="value" fill={color} radius={[6, 6, 0, 0]} />
                </BarChart>
            );
        }
        if (chartType === "area") {
            return (
                <AreaChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5ebe8" />
                    <XAxis dataKey="date" tick={{fontSize: 12}} />
                    <YAxis tick={{fontSize: 12}} />
                    <Tooltip formatter={(value) => formatter ? formatter(Number(value)) : value} />
                    <Area
                        type="monotone"
                        dataKey="value"
                        stroke={color}
                        fill={color}
                        fillOpacity={0.18}
                    />
                </AreaChart>
            );
        }
        return (
            <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5ebe8" />
                <XAxis dataKey="date" tick={{fontSize: 12}} />
                <YAxis tick={{fontSize: 12}} />
                <Tooltip formatter={(value) => formatter ? formatter(Number(value)) : value} />
                <Line
                    type="monotone"
                    dataKey="value"
                    stroke={color}
                    strokeWidth={3}
                    dot={false}
                />
            </LineChart>
        );
    };

    const widgetControls = (widget: DashboardWidgetPreference, index: number) => (
        <div className={styles.widgetControls}>
            {widget.chart_type && (
                <AdminSelect
                    value={widget.chart_type}
                    onChange={(nextValue) =>
                        updateWidget(widget.id, {
                            chart_type: nextValue as DashboardChartType,
                        })
                    }
                    ariaLabel={`${DASHBOARD_WIDGET_LABELS[widget.id] || widget.id} chart type`}
                    options={CHART_TYPES.map((chartType) => ({
                        value: chartType,
                        label: chartType,
                    }))}
                />
            )}
            <AdminSelect
                value={String(widget.timespan_days)}
                onChange={(nextValue) =>
                    updateWidget(widget.id, {
                        timespan_days: Number(nextValue),
                    })
                }
                ariaLabel={`${DASHBOARD_WIDGET_LABELS[widget.id] || widget.id} timespan`}
                options={[
                    {value: "7", label: "7 days"},
                    {value: "14", label: "14 days"},
                    {value: "30", label: "30 days"},
                    {value: "90", label: "90 days"},
                ]}
            />
            <AdminSelect
                value={widget.period}
                onChange={(nextValue) =>
                    updateWidget(widget.id, {
                        period: nextValue as DashboardWidgetPreference["period"],
                    })
                }
                ariaLabel={`${DASHBOARD_WIDGET_LABELS[widget.id] || widget.id} period`}
                options={[
                    {value: "day", label: "Daily"},
                    {value: "week", label: "Weekly"},
                    {value: "month", label: "Monthly"},
                ]}
            />
            <button type="button" onClick={() => moveWidget(widget.id, -1)} disabled={index === 0}>
                Up
            </button>
            <button
                type="button"
                onClick={() => moveWidget(widget.id, 1)}
                disabled={index === sortedWidgets.length - 1}
            >
                Down
            </button>
            <button
                type="button"
                onClick={() => updateWidget(widget.id, {visible: false})}
            >
                Hide
            </button>
            {savingPreference === widget.id && <span>Saving</span>}
        </div>
    );

    const analyticsFor = (widget: DashboardWidgetPreference) =>
        widgetAnalytics[widget.id] || analytics;

    return (
        <section>
            <PanelHeader
                title="Dashboard"
                description="Operational totals for the storefront and catalog."
                actionLabel="Refresh"
                onAction={() => void loadSummary()}
            />
            {isLoading && <InlineState>Loading dashboard.</InlineState>}
            {error && <InlineState tone="error">{error}</InlineState>}
            {!isLoading && !error && analytics && (
                <>
                    {sortedWidgets.some((widget) => !widget.visible) && (
                        <div className={styles.hiddenWidgets}>
                            <span>Hidden widgets</span>
                            {sortedWidgets
                                .filter((widget) => !widget.visible)
                                .map((widget) => (
                                    <button
                                        key={widget.id}
                                        type="button"
                                        onClick={() => updateWidget(widget.id, {visible: true})}
                                    >
                                        Show {DASHBOARD_WIDGET_LABELS[widget.id] || widget.id}
                                    </button>
                                ))}
                        </div>
                    )}
                    <div className={styles.dashboardGrid}>
                        {sortedWidgets
                            .filter((widget) => widget.visible)
                            .map((widget, index) => {
                                const currentAnalytics = analyticsFor(widget);
                                if (!currentAnalytics) {
                                    return null;
                                }
                                if (widget.id === "metrics") {
                                    return (
                                        <ChartPanel
                                            key={widget.id}
                                            title="Metric cards"
                                            controls={widgetControls(widget, index)}
                                        >
                                            <div className={styles.metricGrid}>
                                                {cards.map(([label, value]) => (
                                                    <article key={label} className={styles.metric}>
                                                        <span>{label}</span>
                                                        <strong>{value}</strong>
                                                    </article>
                                                ))}
                                            </div>
                                        </ChartPanel>
                                    );
                                }
                                if (widget.id === "revenue") {
                                    return (
                                        <ChartPanel
                                            key={widget.id}
                                            title="Revenue over time"
                                            controls={widgetControls(widget, index)}
                                        >
                                            <ResponsiveContainer width="100%" height={260}>
                                                {renderSeriesChart(
                                                    currentAnalytics.revenue_over_time,
                                                    widget.chart_type,
                                                    "#2f6f5e",
                                                    (value) => formatPrice(value),
                                                )}
                                            </ResponsiveContainer>
                                        </ChartPanel>
                                    );
                                }
                                if (widget.id === "profit") {
                                    return (
                                        <ChartPanel
                                            key={widget.id}
                                            title="Profit over time"
                                            controls={widgetControls(widget, index)}
                                        >
                                            <ResponsiveContainer width="100%" height={260}>
                                                {renderSeriesChart(
                                                    currentAnalytics.profit_over_time,
                                                    widget.chart_type,
                                                    "#f2ad4b",
                                                    (value) => formatPrice(value),
                                                )}
                                            </ResponsiveContainer>
                                            <div className={styles.compactList}>
                                                <div>
                                                    <span>Estimated profit</span>
                                                    <strong>{formatPrice(currentAnalytics.estimated_profit)}</strong>
                                                </div>
                                                <div>
                                                    <span>Margin</span>
                                                    <strong>{currentAnalytics.profit_margin_percent}%</strong>
                                                </div>
                                            </div>
                                        </ChartPanel>
                                    );
                                }
                                if (widget.id === "orders") {
                                    return (
                                        <ChartPanel
                                            key={widget.id}
                                            title="Orders by day"
                                            controls={widgetControls(widget, index)}
                                        >
                                            <ResponsiveContainer width="100%" height={260}>
                                                {renderSeriesChart(
                                                    currentAnalytics.orders_over_time,
                                                    widget.chart_type,
                                                    "#c84f3f",
                                                )}
                                            </ResponsiveContainer>
                                        </ChartPanel>
                                    );
                                }
                                if (widget.id === "visitors") {
                                    return (
                                        <ChartPanel
                                            key={widget.id}
                                            title="Visitors and page views"
                                            controls={widgetControls(widget, index)}
                                        >
                                            <ResponsiveContainer width="100%" height={260}>
                                                {renderSeriesChart(
                                                    currentAnalytics.visitors_over_time,
                                                    widget.chart_type,
                                                    "#5f6fb2",
                                                )}
                                            </ResponsiveContainer>
                                            <div className={styles.compactList}>
                                                <div>
                                                    <span>Page views over time</span>
                                                    <strong>
                                                        {currentAnalytics.page_views_over_time.reduce(
                                                            (sum, point) => sum + point.value,
                                                            0,
                                                        )} views
                                                    </strong>
                                                </div>
                                            </div>
                                        </ChartPanel>
                                    );
                                }
                                if (widget.id === "status") {
                                    return (
                                        <ChartPanel
                                            key={widget.id}
                                            title="Order status mix"
                                            controls={widgetControls(widget, index)}
                                        >
                                            {currentAnalytics.orders_by_status.length > 0 ? (
                                                <ResponsiveContainer width="100%" height={260}>
                                                    <PieChart>
                                                        <Pie
                                                            data={currentAnalytics.orders_by_status}
                                                            dataKey="count"
                                                            nameKey="status"
                                                            outerRadius={88}
                                                            label
                                                        >
                                                            {currentAnalytics.orders_by_status.map((entry, index) => (
                                                                <Cell
                                                                    key={entry.status}
                                                                    fill={CHART_COLORS[index % CHART_COLORS.length]}
                                                                />
                                                            ))}
                                                        </Pie>
                                                        <Tooltip />
                                                    </PieChart>
                                                </ResponsiveContainer>
                                            ) : (
                                                <InlineState>No orders yet.</InlineState>
                                            )}
                                        </ChartPanel>
                                    );
                                }
                                if (widget.id === "top-products") {
                                    return (
                                        <ChartPanel
                                            key={widget.id}
                                            title="Top products"
                                            controls={widgetControls(widget, index)}
                                        >
                                            {currentAnalytics.top_products.length > 0 ? (
                                                <div className={styles.compactList}>
                                                    {currentAnalytics.top_products.map((product) => (
                                                        <div key={product.name}>
                                                            <span>{product.name}</span>
                                                            <strong>
                                                                {product.quantity} sold - {formatPrice(product.revenue)} revenue - {formatPrice(product.profit)} profit
                                                            </strong>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <InlineState>No product sales yet.</InlineState>
                                            )}
                                        </ChartPanel>
                                    );
                                }
                                if (widget.id === "low-stock") {
                                    return (
                                        <ChartPanel
                                            key={widget.id}
                                            title="Low stock"
                                            controls={widgetControls(widget, index)}
                                        >
                                            {currentAnalytics.low_stock_products.length > 0 ? (
                                                <div className={styles.compactList}>
                                                    {currentAnalytics.low_stock_products.map((product) => (
                                                        <div key={product.product_id}>
                                                            <span>{product.name}</span>
                                                            <strong>{product.stock_quantity} left</strong>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <InlineState>Stock levels look healthy.</InlineState>
                                            )}
                                        </ChartPanel>
                                    );
                                }
                                if (widget.id === "recent-orders") {
                                    return (
                                        <ChartPanel
                                            key={widget.id}
                                            title="Recent orders"
                                            controls={widgetControls(widget, index)}
                                        >
                                            {currentAnalytics.recent_orders.length > 0 ? (
                                                <div className={styles.compactList}>
                                                    {currentAnalytics.recent_orders.map((order) => (
                                                        <div key={order.order_id}>
                                                            <span>{order.email}</span>
                                                            <strong>
                                                                {order.status} - {formatPrice(order.total_price)}
                                                            </strong>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <InlineState>No recent orders.</InlineState>
                                            )}
                                        </ChartPanel>
                                    );
                                }
                                return null;
                            })}
                    </div>
                </>
            )}
        </section>
    );
};

const ChartPanel = ({
    title,
    children,
    controls,
}: {
    title: string;
    children: ReactNode;
    controls?: ReactNode;
}) => (
    <article className={styles.chartPanel}>
        <div className={styles.chartHeader}>
            <h3>{title}</h3>
            {controls}
        </div>
        {children}
    </article>
);

interface PanelHeaderProps {
    title: string;
    description: string;
    actionLabel?: string;
    onAction?: () => void;
}

const PanelHeader = ({title, description, actionLabel, onAction}: PanelHeaderProps) => (
    <header className={styles.panelHeader}>
        <div>
            <p className={styles.eyebrow}>Manage</p>
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
        {actionLabel && onAction && (
            <button type="button" className={styles.secondaryButton} onClick={onAction}>
                {actionLabel}
            </button>
        )}
    </header>
);

const InlineState = ({
    children,
    tone = "neutral",
}: {
    children: string;
    tone?: "neutral" | "error" | "success";
}) => <p className={`${styles.inlineState} ${styles[tone]}`}>{children}</p>;

const ProductsPanel = () => {
    const [products, setProducts] = useState<AdminProduct[]>([]);
    const [query, setQuery] = useState("");
    const [productLanguages, setProductLanguages] = useState<string[]>(
        DEFAULT_PRODUCT_LANGUAGES,
    );
    const [selectedTranslation, setSelectedTranslation] = useState("en");
    const [newLanguage, setNewLanguage] = useState("");
    const [form, setForm] = useState<ProductFormState>(() =>
        emptyProductForm(DEFAULT_PRODUCT_LANGUAGES),
    );
    const [editingProductId, setEditingProductId] = useState<string | null>(null);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [isUploadingImage, setIsUploadingImage] = useState(false);
    const [isDraggingImage, setIsDraggingImage] = useState(false);
    const [isTranslating, setIsTranslating] = useState(false);
    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const formatPrice = useCurrencyFormatter();

    const loadProducts = useCallback(async () => {
        setIsLoading(true);
        setError("");
        try {
            setProducts(await fetchProducts(query));
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to load products."));
        } finally {
            setIsLoading(false);
        }
    }, [query]);

    useEffect(() => {
        const timeoutId = window.setTimeout(() => {
            void loadProducts();
        }, 0);
        return () => window.clearTimeout(timeoutId);
    }, [loadProducts]);

    useEffect(() => {
        const loadProductLanguageSettings = async () => {
            try {
                const settings = await fetchAdminPublicSettings();
                const languages = uniqueLanguageCodes(
                    settings.product_languages.product_languages,
                );
                if (languages.length) {
                    setProductLanguages(languages);
                    setSelectedTranslation((currentLanguage) =>
                        languages.includes(currentLanguage) ? currentLanguage : languages[0],
                    );
                    setForm((currentForm) => ({
                        ...currentForm,
                        translations: ensureProductTranslations(
                            languages,
                            currentForm.translations,
                        ),
                    }));
                }
            } catch {
                setProductLanguages(DEFAULT_PRODUCT_LANGUAGES);
            }
        };

        void loadProductLanguageSettings();
    }, []);

    const resetForm = () => {
        setEditingProductId(null);
        setForm(emptyProductForm(productLanguages));
        setSelectedTranslation(productLanguages[0] || "en");
    };

    const editProduct = async (productId: string) => {
        setError("");
        try {
            const product = await fetchProduct(productId);
            setEditingProductId(productId);
            setForm(productToForm(product, productLanguages));
            setSelectedTranslation(productLanguages[0] || "en");
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to load product."));
        }
    };

    const activeTranslation =
        form.translations.find(
            (translation) => translation.language_code === selectedTranslation,
        ) || form.translations[0];

    const updateTranslation = (
        languageCode: string,
        field: keyof Pick<ProductTranslation, "product_name" | "product_description">,
        value: string,
    ) => {
        setForm((currentForm) => ({
            ...currentForm,
            translations: currentForm.translations.map((translation) =>
                translation.language_code === languageCode
                    ? {...translation, [field]: value}
                    : translation,
            ),
        }));
    };

    const addProductLanguage = () => {
        const languageCode = normalizeLanguageCode(newLanguage);
        const existingCodes = form.translations.map((translation) => translation.language_code);
        setError("");
        setMessage("");

        if (!languageCode) {
            setError("Enter a language code before adding a language.");
            return;
        }

        if (productLanguages.includes(languageCode) || existingCodes.includes(languageCode)) {
            setError(`${languageLabel(languageCode)} is already available for this product.`);
            return;
        }

        const nextLanguages = [...productLanguages, languageCode];
        setProductLanguages(nextLanguages);
        setForm((currentForm) => ({
            ...currentForm,
            translations: ensureProductTranslations(
                nextLanguages,
                currentForm.translations,
            ),
        }));
        setSelectedTranslation(languageCode);
        setNewLanguage("");
        setMessage(`${languageLabel(languageCode)} translation is ready to edit.`);
    };

    const draftMissingTranslations = () => {
        const source =
            form.translations.find((translation) => translation.language_code === "en") ||
            form.translations[0];
        setForm((currentForm) => ({
            ...currentForm,
            translations: currentForm.translations.map((translation) => {
                if (
                    translation.product_name.trim() &&
                    translation.product_description.trim()
                ) {
                    return translation;
                }
                return {
                    ...translation,
                    product_name: translation.product_name.trim()
                        ? translation.product_name
                        : draftTranslation(translation.language_code, source).product_name,
                    product_description: translation.product_description.trim()
                        ? translation.product_description
                        : source?.product_description || "",
                };
            }),
        }));
    };

    const applyTranslationPreview = async (targetLanguages: string[]) => {
        const source =
            form.translations.find((translation) => translation.language_code === "en") ||
            form.translations[0];
        if (!source?.product_name.trim() || !source.product_description.trim()) {
            setError("Add an English name and description before translating.");
            return;
        }
        const filledTargets = form.translations.filter(
            (translation) =>
                targetLanguages.includes(translation.language_code) &&
                translation.language_code !== "en" &&
                (translation.product_name.trim() ||
                    translation.product_description.trim()),
        );
        if (
            filledTargets.length > 0 &&
            !window.confirm("Replace existing translated text for the selected language?")
        ) {
            return;
        }
        setIsTranslating(true);
        setMessage("");
        setError("");
        try {
            const preview = await previewProductTranslations(
                form.translations,
                targetLanguages,
            );
            if (preview.translations.length === 0) {
                setMessage("No translations needed.");
                return;
            }
            const unavailable = preview.translations.filter(
                (translation) => translation.provider_status === "unavailable",
            );
            setForm((currentForm) => {
                const translationsByLanguage = new Map(
                    currentForm.translations.map((translation) => [
                        translation.language_code,
                        translation,
                    ]),
                );
                preview.translations.forEach((translation) => {
                    if (translation.provider_status === "unavailable") {
                        return;
                    }
                    translationsByLanguage.set(translation.language_code, {
                        language_code: translation.language_code,
                        product_name: translation.product_name,
                        product_description: translation.product_description,
                    });
                });
                return {
                    ...currentForm,
                    translations: ensureProductTranslations(
                        productLanguages,
                        Array.from(translationsByLanguage.values()),
                    ),
                };
            });
            setMessage(
                unavailable.length
                    ? "Some translations were unavailable; manual editing is still available."
                    : "Translations generated. Review them before saving.",
            );
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to translate product."));
        } finally {
            setIsTranslating(false);
        }
    };

    const translateMissingTranslations = () => {
        const missingLanguages = form.translations
            .filter(
                (translation) =>
                    translation.language_code !== "en" &&
                    (!translation.product_name.trim() ||
                        !translation.product_description.trim()),
            )
            .map((translation) => translation.language_code);
        if (missingLanguages.length === 0) {
            draftMissingTranslations();
            setMessage("Translations already have content.");
            return;
        }
        void applyTranslationPreview(missingLanguages);
    };

    const regenerateActiveTranslation = () => {
        if (!activeTranslation || activeTranslation.language_code === "en") {
            setMessage("Choose a non-English language to regenerate.");
            return;
        }
        void applyTranslationPreview([activeTranslation.language_code]);
    };

    const submitProduct = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setIsSaving(true);
        setMessage("");
        setError("");
        try {
            if (editingProductId) {
                await updateProduct(editingProductId, form);
                setMessage("Product updated.");
            } else {
                await createProduct(form);
                setMessage("Product created.");
            }
            resetForm();
            await loadProducts();
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to save product."));
        } finally {
            setIsSaving(false);
        }
    };

    const removeProduct = async (productId: string) => {
        if (!window.confirm("Delete this product?")) {
            return;
        }
        setError("");
        try {
            await deleteProduct(productId);
            setMessage("Product deleted.");
            await loadProducts();
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to delete product."));
        }
    };

    const runSeed = async () => {
        setMessage("");
        setError("");
        try {
            const result = await seedProducts();
            setMessage(
                `Seed complete: ${result.created} created, ${result.updated} updated, ${result.skipped} unchanged.`,
            );
            await loadProducts();
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to seed products."));
        }
    };

    const uploadImage = async (file: File | undefined) => {
        if (!file) {
            return;
        }
        setIsUploadingImage(true);
        setError("");
        try {
            const media = await uploadProductImage(file);
            setForm((currentForm) => ({...currentForm, image_src: media.url}));
            setMessage("Product image uploaded.");
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to upload image."));
        } finally {
            setIsUploadingImage(false);
        }
    };

    const handleImageDrop = (event: DragEvent<HTMLButtonElement>) => {
        event.preventDefault();
        setIsDraggingImage(false);
        void uploadImage(event.dataTransfer.files?.[0]);
    };

    return (
        <section>
            <PanelHeader
                title="Products"
                description="Search, seed, create, edit, and remove catalog items."
                actionLabel="Seed catalog"
                onAction={() => void runSeed()}
            />
            <div className={styles.toolbar}>
                <label>
                    Search products
                    <input
                        value={query}
                        onChange={(event) => setQuery(event.target.value)}
                        placeholder="Name or translation"
                    />
                </label>
                <button type="button" className={styles.secondaryButton} onClick={() => void loadProducts()}>
                    Search
                </button>
            </div>
            {message && <InlineState tone="success">{message}</InlineState>}
            {error && <InlineState tone="error">{error}</InlineState>}
            <div className={styles.splitGrid}>
                <form className={styles.formPanel} onSubmit={submitProduct}>
                    <h3>{editingProductId ? "Edit product" : "Create product"}</h3>
                    <div className={styles.translationPanel}>
                        <div className={styles.translationHeader}>
                            <div>
                                <strong>Translations</strong>
                                <span>Each language can be edited before publishing.</span>
                            </div>
                            <button
                                type="button"
                                className={styles.secondaryButton}
                                onClick={translateMissingTranslations}
                                disabled={isTranslating}
                            >
                                {isTranslating ? "Translating" : "Translate missing"}
                            </button>
                        </div>
                        <div className={styles.languageTabs} role="tablist" aria-label="Product translations">
                            {form.translations.map((translation) => (
                                <button
                                    key={translation.language_code}
                                    type="button"
                                    role="tab"
                                    aria-selected={
                                        translation.language_code === selectedTranslation
                                    }
                                    className={
                                        translation.language_code === selectedTranslation
                                            ? styles.languageActive
                                            : styles.languageButton
                                    }
                                    onClick={() =>
                                        setSelectedTranslation(translation.language_code)
                                    }
                                >
                                    {languageLabel(translation.language_code)}
                                </button>
                            ))}
                        </div>
                        <div className={styles.translationTools}>
                            <label className={styles.compactField}>
                                New language
                                <input
                                    value={newLanguage}
                                    onChange={(event) => setNewLanguage(event.target.value)}
                                    placeholder="Language code, for example de"
                                    aria-label="New product language code"
                                />
                            </label>
                            <button type="button" className={styles.secondaryButton} onClick={addProductLanguage}>
                                Add language
                            </button>
                            <button
                                type="button"
                                className={styles.secondaryButton}
                                onClick={regenerateActiveTranslation}
                                disabled={isTranslating || activeTranslation?.language_code === "en"}
                            >
                                Regenerate selected
                            </button>
                        </div>
                        {activeTranslation && (
                            <div className={styles.translationFields}>
                                <label>
                                    {languageLabel(activeTranslation.language_code)} name
                                    <input
                                        value={activeTranslation.product_name}
                                        onChange={(event) =>
                                            updateTranslation(
                                                activeTranslation.language_code,
                                                "product_name",
                                                event.target.value,
                                            )
                                        }
                                        required
                                    />
                                </label>
                                <label>
                                    {languageLabel(activeTranslation.language_code)} description
                                    <textarea
                                        value={activeTranslation.product_description}
                                        onChange={(event) =>
                                            updateTranslation(
                                                activeTranslation.language_code,
                                                "product_description",
                                                event.target.value,
                                            )
                                        }
                                        required
                                    />
                                </label>
                            </div>
                        )}
                    </div>
                    <div className={styles.formGrid}>
                        <label>
                            Price
                            <input
                                type="number"
                                min="0.01"
                                step="0.01"
                                value={form.price}
                                onChange={(event) => setForm({...form, price: event.target.value})}
                                required
                            />
                        </label>
                        <label>
                            Cost
                            <input
                                type="number"
                                min="0"
                                step="0.01"
                                value={form.cost_price}
                                onChange={(event) => setForm({...form, cost_price: event.target.value})}
                                placeholder="Production cost in UAH"
                            />
                        </label>
                        <label>
                            Stock
                            <input
                                type="number"
                                min="0"
                                value={form.stock_quantity}
                                onChange={(event) => setForm({...form, stock_quantity: event.target.value})}
                                required
                            />
                        </label>
                        <div className={styles.selectField}>
                            <span>Category</span>
                            <AdminSelect
                                value={form.category}
                                onChange={(nextValue) => setForm({...form, category: nextValue})}
                                ariaLabel="Product category"
                                options={[
                                    {value: "Chebureks", label: "Chebureks"},
                                    {value: "Pies", label: "Pies"},
                                    {value: "Drinks", label: "Drinks"},
                                    {value: "Other", label: "Other"},
                                ]}
                            />
                        </div>
                        <label className={styles.fullWidth}>
                            Tags
                            <input
                                value={form.tags}
                                onChange={(event) => setForm({...form, tags: event.target.value})}
                                placeholder="meat, spicy, lunch"
                            />
                        </label>
                    </div>
                    <button
                        type="button"
                        className={`${styles.mediaDropzone} ${isDraggingImage ? styles.mediaDropzoneActive : ""}`}
                        onClick={() => fileInputRef.current?.click()}
                        onDragOver={(event) => {
                            event.preventDefault();
                            setIsDraggingImage(true);
                        }}
                        onDragLeave={() => setIsDraggingImage(false)}
                        onDrop={handleImageDrop}
                    >
                        <img
                            src={form.image_src || categoryFallbackSvg(form.category)}
                            alt="Product preview"
                            onError={(event) => {
                                event.currentTarget.src = categoryFallbackSvg(form.category);
                            }}
                        />
                        <span>
                            {isUploadingImage
                                ? "Uploading image"
                                : "Drop product image here or click to upload"}
                        </span>
                        <small>PNG, JPEG, WebP, GIF, or SVG. Stored in local media storage.</small>
                    </button>
                    <input
                        ref={fileInputRef}
                        className={styles.hiddenFileInput}
                        type="file"
                        accept="image/png,image/jpeg,image/webp,image/gif,image/svg+xml"
                        onChange={(event) => void uploadImage(event.target.files?.[0])}
                    />
                    <div className={styles.formActions}>
                        <button type="submit" className={styles.primaryButton} disabled={isSaving || isUploadingImage}>
                            {isSaving ? "Saving" : editingProductId ? "Update product" : "Create product"}
                        </button>
                        {editingProductId && (
                            <button type="button" className={styles.secondaryButton} onClick={resetForm}>
                                Cancel
                            </button>
                        )}
                    </div>
                </form>

                <div className={styles.tablePanel}>
                    {isLoading && <InlineState>Loading products.</InlineState>}
                    {!isLoading && products.length === 0 && <InlineState>No products found.</InlineState>}
                    {!isLoading && products.length > 0 && (
                        <ResponsiveTable
                            headers={["Product", "Category", "Tags", "Price", "Cost", "Stock", "Actions"]}
                            rows={products.map((product) => [
                                <div className={styles.productCell}>
                                    <img
                                        src={product.image_src || categoryFallbackSvg(product.category)}
                                        alt=""
                                        onError={(event) => {
                                            event.currentTarget.src = categoryFallbackSvg(product.category);
                                        }}
                                    />
                                    <strong>{product.name}</strong>
                                </div>,
                                product.category,
                                <span className={styles.tagList}>
                                    {product.tags?.length ? product.tags.join(", ") : "No tags"}
                                </span>,
                                formatPrice(product.price),
                                formatPrice(product.cost_price || 0),
                                product.stock_quantity,
                                <div className={styles.rowActions}>
                                    <button type="button" onClick={() => void editProduct(product.product_id)}>
                                        Edit
                                    </button>
                                    <button type="button" onClick={() => void removeProduct(product.product_id)}>
                                        Delete
                                    </button>
                                </div>,
                            ])}
                        />
                    )}
                </div>
            </div>
        </section>
    );
};

const OrdersPanel = () => {
    const [orders, setOrders] = useState<AdminOrder[]>([]);
    const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
    const [adminNotes, setAdminNotes] = useState("");
    const [filters, setFilters] = useState({
        q: "",
        status: "" as OrderStatus | "",
        date_from: "",
        date_to: "",
    });
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const formatPrice = useCurrencyFormatter();

    const selectedOrder = useMemo(
        () => orders.find((order) => order.order_id === selectedOrderId) || orders[0],
        [orders, selectedOrderId],
    );

    useEffect(() => {
        const timeoutId = window.setTimeout(() => {
            setAdminNotes(selectedOrder?.admin_notes || "");
        }, 0);
        return () => window.clearTimeout(timeoutId);
    }, [selectedOrder?.order_id, selectedOrder?.admin_notes]);

    const loadOrders = useCallback(async () => {
        setIsLoading(true);
        setError("");
        try {
            const nextOrders = await fetchOrders(filters);
            setOrders(nextOrders);
            setSelectedOrderId((previousId) => previousId || nextOrders[0]?.order_id || null);
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to load orders."));
        } finally {
            setIsLoading(false);
        }
    }, [filters]);

    useEffect(() => {
        const timeoutId = window.setTimeout(() => {
            void loadOrders();
        }, 0);
        return () => window.clearTimeout(timeoutId);
    }, [loadOrders]);

    const changeStatus = async (orderId: string, status: OrderStatus) => {
        setError("");
        setMessage("");
        try {
            await updateOrderStatus(orderId, status);
            setMessage("Order status updated.");
            await loadOrders();
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to update order."));
        }
    };

    const removeOrder = async (orderId: string) => {
        if (!window.confirm("Delete this order?")) {
            return;
        }
        setError("");
        try {
            await deleteOrder(orderId);
            setMessage("Order deleted.");
            setSelectedOrderId(null);
            await loadOrders();
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to delete order."));
        }
    };

    const saveOrderNotes = async (orderId: string) => {
        setError("");
        setMessage("");
        try {
            await updateOrderNotes(orderId, adminNotes);
            setMessage("Order notes updated.");
            await loadOrders();
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to update order notes."));
        }
    };

    return (
        <section>
            <PanelHeader
                title="Orders"
                description="Review order contents and keep fulfillment status current."
                actionLabel="Refresh"
                onAction={() => void loadOrders()}
            />
            {message && <InlineState tone="success">{message}</InlineState>}
            {error && <InlineState tone="error">{error}</InlineState>}
            <div className={styles.filterBar}>
                <label>
                    Search orders
                    <input
                        value={filters.q}
                        onChange={(event) => setFilters({...filters, q: event.target.value})}
                        placeholder="Email, order id, product, or notes"
                    />
                </label>
                <div className={styles.selectField}>
                    <span>Status</span>
                    <AdminSelect
                        value={filters.status}
                        onChange={(nextValue) =>
                            setFilters({...filters, status: nextValue as OrderStatus | ""})
                        }
                        ariaLabel="Order status filter"
                        options={[
                            {value: "", label: "All statuses"},
                            ...ORDER_STATUSES.map((status) => ({
                                value: status,
                                label: status,
                            })),
                        ]}
                    />
                </div>
                <label>
                    From
                    <input
                        type="date"
                        value={filters.date_from}
                        onChange={(event) => setFilters({...filters, date_from: event.target.value})}
                    />
                </label>
                <label>
                    To
                    <input
                        type="date"
                        value={filters.date_to}
                        onChange={(event) => setFilters({...filters, date_to: event.target.value})}
                    />
                </label>
                <button type="button" className={styles.secondaryButton} onClick={() => void loadOrders()}>
                    Search
                </button>
            </div>
            {isLoading && <InlineState>Loading orders.</InlineState>}
            {!isLoading && orders.length === 0 && <InlineState>No orders yet.</InlineState>}
            {!isLoading && orders.length > 0 && (
                <div className={styles.splitGrid}>
                    <div className={styles.tablePanel}>
                        <ResponsiveTable
                            headers={["Customer", "Status", "Total", "Created"]}
                            rows={orders.map((order) => [
                                <button
                                    type="button"
                                    className={styles.linkButton}
                                    onClick={() => setSelectedOrderId(order.order_id)}
                                >
                                    {order.email}
                                </button>,
                                <span className={styles.statusChip}>{order.status}</span>,
                                formatPrice(order.total_price || 0),
                                new Date(order.created_at).toLocaleString(),
                            ])}
                        />
                    </div>
                    {selectedOrder && (
                        <article className={styles.detailPanel}>
                            <div className={styles.detailHeader}>
                                <div>
                                    <p className={styles.eyebrow}>Order</p>
                                    <h3>{selectedOrder.email}</h3>
                                </div>
                                <button
                                    type="button"
                                    className={styles.dangerButton}
                                    onClick={() => void removeOrder(selectedOrder.order_id)}
                                >
                                    Delete
                                </button>
                            </div>
                            <div className={styles.selectField}>
                                <span>Status</span>
                                <AdminSelect
                                    value={selectedOrder.status}
                                    onChange={(nextValue) =>
                                        void changeStatus(
                                            selectedOrder.order_id,
                                            nextValue as OrderStatus,
                                        )
                                    }
                                    ariaLabel="Selected order status"
                                    options={ORDER_STATUSES.map((status) => ({
                                        value: status,
                                        label: status,
                                    }))}
                                />
                            </div>
                            <div className={styles.orderAddress}>
                                <strong>Delivery</strong>
                                <span>
                                    {selectedOrder.address.street_number} {selectedOrder.address.street_name},{" "}
                                    {selectedOrder.address.city}, {selectedOrder.address.state}
                                </span>
                            </div>
                            <div className={styles.orderAddress}>
                                <strong>Customer notes</strong>
                                <span>{selectedOrder.customer_notes || "No customer notes."}</span>
                            </div>
                            <label>
                                Private admin notes
                                <textarea
                                    value={adminNotes}
                                    onChange={(event) => setAdminNotes(event.target.value)}
                                    placeholder="Fulfillment handoff, delivery context, or customer follow-up"
                                />
                            </label>
                            <button
                                type="button"
                                className={styles.secondaryButton}
                                onClick={() => void saveOrderNotes(selectedOrder.order_id)}
                            >
                                Save notes
                            </button>
                            <div className={styles.orderItems}>
                                {selectedOrder.products.map((product) => (
                                    <div key={`${selectedOrder.order_id}-${product.name}`} className={styles.orderItem}>
                                        <span>{product.name}</span>
                                        <span>
                                            {product.quantity} x {formatPrice(product.price)}
                                            {product.cost_price > 0
                                                ? ` · profit ${formatPrice((product.price - product.cost_price) * product.quantity)}`
                                                : ""}
                                        </span>
                                    </div>
                                ))}
                                <div className={styles.orderItemTotal}>
                                    <span>Total</span>
                                    <strong>{formatPrice(selectedOrder.total_price || 0)}</strong>
                                </div>
                            </div>
                        </article>
                    )}
                </div>
            )}
        </section>
    );
};

const UsersPanel = ({currentUser}: {currentUser: AdminUser}) => {
    const [users, setUsers] = useState<AdminUser[]>([]);
    const [filters, setFilters] = useState({
        q: "",
        is_active: "" as boolean | "",
        is_verified: "" as boolean | "",
        is_superuser: "" as boolean | "",
    });
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [flags, setFlags] = useState({
        is_active: true,
        is_verified: true,
        is_superuser: false,
    });
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [isLoading, setIsLoading] = useState(true);

    const loadUsers = useCallback(async () => {
        setIsLoading(true);
        setError("");
        try {
            setUsers(await fetchUsers(filters));
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to load users."));
        } finally {
            setIsLoading(false);
        }
    }, [filters]);

    useEffect(() => {
        const timeoutId = window.setTimeout(() => {
            void loadUsers();
        }, 0);
        return () => window.clearTimeout(timeoutId);
    }, [loadUsers]);

    const submitUser = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError("");
        setMessage("");
        try {
            await createUser(email, password, flags);
            setEmail("");
            setPassword("");
            setFlags({is_active: true, is_verified: true, is_superuser: false});
            setMessage("User created.");
            await loadUsers();
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to create user."));
        }
    };

    const toggleFlag = async (
        user: AdminUser,
        field: "is_active" | "is_superuser" | "is_verified",
    ) => {
        setError("");
        setMessage("");
        try {
            await updateUserFlags(user.id, {
                is_active: field === "is_active" ? !user.is_active : user.is_active,
                is_superuser:
                    field === "is_superuser" ? !user.is_superuser : user.is_superuser,
                is_verified: field === "is_verified" ? !user.is_verified : user.is_verified,
            });
            setMessage("User updated.");
            await loadUsers();
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to update user."));
        }
    };

    const removeUser = async (user: AdminUser) => {
        if (user.id === currentUser.id) {
            setError("You cannot delete the signed-in admin account.");
            return;
        }
        if (!window.confirm("Delete this user?")) {
            return;
        }
        setError("");
        try {
            await deleteUser(user.id);
            setMessage("User deleted.");
            await loadUsers();
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to delete user."));
        }
    };

    return (
        <section>
            <PanelHeader
                title="Users"
                description="Create users and manage active, verified, and superuser flags."
                actionLabel="Refresh"
                onAction={() => void loadUsers()}
            />
            {message && <InlineState tone="success">{message}</InlineState>}
            {error && <InlineState tone="error">{error}</InlineState>}
            <div className={styles.filterBar}>
                <label>
                    Search users
                    <input
                        value={filters.q}
                        onChange={(event) => setFilters({...filters, q: event.target.value})}
                        placeholder="Email address"
                    />
                </label>
                {(["is_active", "is_verified", "is_superuser"] as const).map((field) => (
                    <div className={styles.selectField} key={field}>
                        <span>{field.replace("is_", "").replace("_", " ")}</span>
                        <AdminSelect
                            value={String(filters[field])}
                            onChange={(value) => {
                                setFilters({
                                    ...filters,
                                    [field]: value === "" ? "" : value === "true",
                                });
                            }}
                            ariaLabel={`${field.replace("is_", "").replace("_", " ")} filter`}
                            options={[
                                {value: "", label: "Any"},
                                {value: "true", label: "Yes"},
                                {value: "false", label: "No"},
                            ]}
                        />
                    </div>
                ))}
                <button type="button" className={styles.secondaryButton} onClick={() => void loadUsers()}>
                    Search
                </button>
            </div>
            <div className={styles.splitGrid}>
                <form className={styles.formPanel} onSubmit={submitUser}>
                    <h3>Create user</h3>
                    <label>
                        Email
                        <input
                            type="email"
                            value={email}
                            onChange={(event) => setEmail(event.target.value)}
                            required
                        />
                    </label>
                    <label>
                        Password
                        <input
                            type="password"
                            minLength={8}
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                            required
                        />
                    </label>
                    <div className={styles.checkGroup}>
                        <label>
                            <input
                                type="checkbox"
                                checked={flags.is_active}
                                onChange={(event) => setFlags({...flags, is_active: event.target.checked})}
                            />
                            Active
                        </label>
                        <label>
                            <input
                                type="checkbox"
                                checked={flags.is_verified}
                                onChange={(event) => setFlags({...flags, is_verified: event.target.checked})}
                            />
                            Verified
                        </label>
                        <label>
                            <input
                                type="checkbox"
                                checked={flags.is_superuser}
                                onChange={(event) => setFlags({...flags, is_superuser: event.target.checked})}
                            />
                            Superuser
                        </label>
                    </div>
                    <button type="submit" className={styles.primaryButton}>
                        Create user
                    </button>
                </form>
                <div className={styles.tablePanel}>
                    {isLoading && <InlineState>Loading users.</InlineState>}
                    {!isLoading && users.length === 0 && <InlineState>No users found.</InlineState>}
                    {!isLoading && users.length > 0 && (
                        <ResponsiveTable
                            headers={["Email", "Active", "Verified", "Superuser", "Actions"]}
                            rows={users.map((user) => [
                                <strong>{user.email}</strong>,
                                <FlagButton enabled={user.is_active} onClick={() => void toggleFlag(user, "is_active")} />,
                                <FlagButton enabled={user.is_verified} onClick={() => void toggleFlag(user, "is_verified")} />,
                                <FlagButton
                                    enabled={user.is_superuser}
                                    onClick={() => void toggleFlag(user, "is_superuser")}
                                />,
                                <button
                                    type="button"
                                    className={styles.dangerTextButton}
                                    onClick={() => void removeUser(user)}
                                    disabled={user.id === currentUser.id}
                                >
                                    Delete
                                </button>,
                            ])}
                        />
                    )}
                </div>
            </div>
        </section>
    );
};

const SettingsPanel = () => {
    const dispatch = useAppDispatch();
    const currentCurrency = useAppSelector((state) => state.settings.currency);
    const [defaultCurrency, setDefaultCurrency] = useState(currentCurrency.default_currency);
    const [baseCurrency, setBaseCurrency] = useState(currentCurrency.base_currency);
    const [supportedInput, setSupportedInput] = useState(
        currentCurrency.supported_currencies.join(","),
    );
    const [rates, setRates] = useState<Record<string, string>>(
        Object.fromEntries(
            Object.entries(currentCurrency.currency_rates).map(([currencyCode, rate]) => [
                currencyCode,
                String(rate),
            ]),
        ),
    );
    const [symbols, setSymbols] = useState<Record<string, string>>(
        currentCurrency.currency_symbols,
    );
    const [languageInput, setLanguageInput] = useState(DEFAULT_PRODUCT_LANGUAGES.join(","));
    const [autoTranslateProducts, setAutoTranslateProducts] = useState(true);
    const [fallbackProfitMargin, setFallbackProfitMargin] = useState("0.35");
    const [translationStatus, setTranslationStatus] = useState("unknown");
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [isSaving, setIsSaving] = useState(false);
    const [isSavingLanguages, setIsSavingLanguages] = useState(false);
    const [isBackfillingTranslations, setIsBackfillingTranslations] = useState(false);

    const supportedCurrencies = useMemo(
        () =>
            supportedInput
                .split(",")
                .map((currencyCode) => currencyCode.trim().toUpperCase())
                .filter(Boolean),
        [supportedInput],
    );

    const productLanguages = useMemo(
        () => uniqueLanguageCodes(languageInput.split(",")),
        [languageInput],
    );

    const loadSettings = useCallback(async () => {
        setError("");
        try {
            const settings = await fetchAdminPublicSettings();
            setBaseCurrency(settings.currency.base_currency);
            setDefaultCurrency(settings.currency.default_currency);
            setSupportedInput(settings.currency.supported_currencies.join(","));
            setRates(
                Object.fromEntries(
                    Object.entries(settings.currency.currency_rates).map(
                        ([currencyCode, rate]) => [currencyCode, String(rate)],
                    ),
                ),
            );
            setSymbols(settings.currency.currency_symbols);
            setLanguageInput(settings.product_languages.product_languages.join(","));
            setAutoTranslateProducts(settings.product_languages.auto_translate_products);
            setFallbackProfitMargin(String(settings.profit.fallback_profit_margin));
            setTranslationStatus(settings.translation.status);
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to load settings."));
        }
    }, []);

    useEffect(() => {
        const timeoutId = window.setTimeout(() => {
            void loadSettings();
        }, 0);
        return () => window.clearTimeout(timeoutId);
    }, [loadSettings]);

    const submitSettings = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setIsSaving(true);
        setMessage("");
        setError("");

        const payload: CurrencySettingsUpdate = {
            default_currency: defaultCurrency,
            supported_currencies: supportedCurrencies,
            currency_rates: Object.fromEntries(
                supportedCurrencies.map((currencyCode) => [
                    currencyCode,
                    Number(rates[currencyCode] || 0),
                ]),
            ),
            currency_symbols: Object.fromEntries(
                supportedCurrencies.map((currencyCode) => [
                    currencyCode,
                    symbols[currencyCode] || currencyCode,
                ]),
            ),
        };

        try {
            await updateCurrencySettings(payload);
            await dispatch(refreshPublicSettings());
            setMessage("Currency settings updated.");
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to save settings."));
        } finally {
            setIsSaving(false);
        }
    };

    const submitLanguageSettings = async () => {
        setIsSavingLanguages(true);
        setMessage("");
        setError("");

        try {
            await updateProductLanguageSettings({
                product_languages: productLanguages,
                auto_translate_products: autoTranslateProducts,
            });
            setMessage("Product language settings updated.");
        } catch (requestError) {
            setError(
                getAdminErrorMessage(
                    requestError,
                    "Unable to save product language settings.",
                ),
            );
        } finally {
            setIsSavingLanguages(false);
        }
    };

    const submitProfitSettings = async () => {
        setIsSaving(true);
        setMessage("");
        setError("");

        try {
            await updateProfitSettings(Number(fallbackProfitMargin));
            setMessage("Profit assumptions updated.");
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to save profit settings."));
        } finally {
            setIsSaving(false);
        }
    };

    const runTranslationBackfill = async () => {
        setIsBackfillingTranslations(true);
        setMessage("");
        setError("");

        try {
            const result = await backfillProductTranslations();
            setMessage(
                `Translation backfill complete: ${result.translations_created} created across ${result.products_scanned} products.`,
            );
        } catch (requestError) {
            setError(
                getAdminErrorMessage(
                    requestError,
                    "Unable to backfill product translations.",
                ),
            );
        } finally {
            setIsBackfillingTranslations(false);
        }
    };

    return (
        <section>
            <PanelHeader
                title="Settings"
                description="Manage currency, product language coverage, and catalog translation behavior."
                actionLabel="Reload"
                onAction={() => void loadSettings()}
            />
            {message && <InlineState tone="success">{message}</InlineState>}
            {error && <InlineState tone="error">{error}</InlineState>}
            <div className={styles.settingsSections}>
                <form className={styles.settingsPanel} onSubmit={submitSettings}>
                    <div className={styles.settingsPanelHeader}>
                        <div>
                            <p className={styles.eyebrow}>Display</p>
                            <h3>Currency</h3>
                        </div>
                        <span>Controls storefront and CMS price formatting.</span>
                    </div>
                    <div className={styles.formGrid}>
                        <label>
                            Base currency
                            <input value={baseCurrency} disabled />
                        </label>
                        <div className={styles.selectField}>
                            <span>Default display currency</span>
                            <AdminSelect
                                value={defaultCurrency}
                                onChange={setDefaultCurrency}
                                ariaLabel="Default display currency"
                                options={supportedCurrencies.map((currencyCode) => ({
                                    value: currencyCode,
                                    label: currencyCode,
                                }))}
                            />
                        </div>
                        <label>
                            Supported currencies
                            <input
                                value={supportedInput}
                                onChange={(event) => setSupportedInput(event.target.value)}
                                placeholder="UAH,USD,EUR"
                            />
                        </label>
                    </div>
                    <div className={styles.currencyGrid}>
                        {supportedCurrencies.map((currencyCode) => (
                            <div key={currencyCode} className={styles.currencyRow}>
                                <strong>{currencyCode}</strong>
                                <label>
                                    Rate from UAH
                                    <input
                                        type="number"
                                        min="0.0001"
                                        step="0.0001"
                                        value={rates[currencyCode] ?? ""}
                                        onChange={(event) =>
                                            setRates({...rates, [currencyCode]: event.target.value})
                                        }
                                        required
                                    />
                                </label>
                                <label>
                                    Symbol
                                    <input
                                        value={symbols[currencyCode] ?? ""}
                                        onChange={(event) =>
                                            setSymbols({...symbols, [currencyCode]: event.target.value})
                                        }
                                        required
                                    />
                                </label>
                            </div>
                        ))}
                    </div>
                    <button type="submit" className={styles.primaryButton} disabled={isSaving}>
                        {isSaving ? "Saving" : "Save currency"}
                    </button>
                </form>
                <div className={styles.settingsPanel}>
                    <div className={styles.settingsPanelHeader}>
                        <div>
                            <p className={styles.eyebrow}>Finance</p>
                            <h3>Profit assumptions</h3>
                        </div>
                        <span>Used only when older order lines do not have a saved cost.</span>
                    </div>
                    <div className={styles.formGrid}>
                        <label>
                            Fallback profit margin
                            <input
                                type="number"
                                min="0"
                                max="1"
                                step="0.01"
                                value={fallbackProfitMargin}
                                onChange={(event) => setFallbackProfitMargin(event.target.value)}
                            />
                        </label>
                        <div className={styles.settingsPreview}>
                            <span>Example</span>
                            <strong>{Math.round(Number(fallbackProfitMargin || 0) * 100)}% estimated margin</strong>
                        </div>
                    </div>
                    <button
                        type="button"
                        className={styles.primaryButton}
                        disabled={isSaving}
                        onClick={() => void submitProfitSettings()}
                    >
                        {isSaving ? "Saving" : "Save profit settings"}
                    </button>
                </div>
                <div className={styles.settingsPanel}>
                    <div className={styles.settingsPanelHeader}>
                        <div>
                            <p className={styles.eyebrow}>Catalog</p>
                            <h3>Product languages</h3>
                        </div>
                        <span className={translationStatus === "ok" ? styles.statusGood : styles.statusWarning}>
                            Translator: {translationStatus}
                        </span>
                    </div>
                    <div className={styles.formGrid}>
                        <label>
                            Language codes
                            <input
                                value={languageInput}
                                onChange={(event) => setLanguageInput(event.target.value)}
                                placeholder="en,ukr,de"
                            />
                        </label>
                        <label className={styles.checkLine}>
                            <input
                                type="checkbox"
                                checked={autoTranslateProducts}
                                onChange={(event) =>
                                    setAutoTranslateProducts(event.target.checked)
                                }
                            />
                            Draft missing translations for new products
                        </label>
                    </div>
                    <p className={styles.settingsHint}>
                        New languages are added as editable draft translations. Existing
                        products can be backfilled without deleting catalog data.
                    </p>
                    <div className={styles.formActions}>
                        <button
                            type="button"
                            className={styles.primaryButton}
                            disabled={isSavingLanguages || productLanguages.length === 0}
                            onClick={() => void submitLanguageSettings()}
                        >
                            {isSavingLanguages ? "Saving" : "Save languages"}
                        </button>
                        <button
                            type="button"
                            className={styles.secondaryButton}
                            disabled={isBackfillingTranslations}
                            onClick={() => void runTranslationBackfill()}
                        >
                            {isBackfillingTranslations ? "Backfilling" : "Backfill products"}
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
};

const FlagButton = ({enabled, onClick}: {enabled: boolean; onClick: () => void}) => (
    <button type="button" className={enabled ? styles.flagOn : styles.flagOff} onClick={onClick}>
        {enabled ? "Yes" : "No"}
    </button>
);

const ResponsiveTable = ({
    headers,
    rows,
}: {
    headers: string[];
    rows: Array<Array<ReactNode>>;
}) => (
    <div className={styles.tableScroller}>
        <table className={styles.table}>
            <thead>
                <tr>
                    {headers.map((header) => (
                        <th key={header}>{header}</th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {rows.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                        {row.map((cell, cellIndex) => (
                            <td key={`${rowIndex}-${cellIndex}`}>{cell}</td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
);

export default AdminApp;
