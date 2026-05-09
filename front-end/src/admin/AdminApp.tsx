import {FormEvent, ReactNode, useCallback, useEffect, useMemo, useState} from "react";

import {
    ADMIN_TOKEN_KEY,
    clearAdminToken,
    createProduct,
    createUser,
    deleteOrder,
    deleteProduct,
    deleteUser,
    fetchAdminMe,
    fetchAdminSummary,
    fetchOrders,
    fetchProduct,
    fetchProducts,
    fetchUsers,
    getAdminErrorMessage,
    loginAdmin,
    seedProducts,
    updateOrderStatus,
    updateProduct,
    updateUserFlags,
} from "./api.ts";
import styles from "./AdminApp.module.scss";
import type {
    AdminOrder,
    AdminProduct,
    AdminSummary,
    AdminUser,
    AdminView,
    OrderStatus,
    ProductFormState,
} from "./types.ts";

const ORDER_STATUSES: OrderStatus[] = [
    "PENDING",
    "CONFIRMED",
    "PREPARING",
    "READY",
    "DELIVERED",
    "CANCELLED",
];

const emptyProductForm = (): ProductFormState => ({
    price: "",
    category: "Chebureks",
    stock_quantity: "0",
    image_src: "",
    en_name: "",
    en_description: "",
    ukr_name: "",
    ukr_description: "",
});

const productToForm = (product: AdminProduct): ProductFormState => {
    const englishTranslation = product.translations?.find(
        (translation) => translation.language_code === "en",
    );
    const ukrainianTranslation = product.translations?.find(
        (translation) => translation.language_code === "ukr",
    );

    return {
        price: String(product.price),
        category: product.category || "Chebureks",
        stock_quantity: String(product.stock_quantity),
        image_src: product.image_src,
        en_name: englishTranslation?.product_name || product.name || "",
        en_description: englishTranslation?.product_description || product.description || "",
        ukr_name: ukrainianTranslation?.product_name || "",
        ukr_description: ukrainianTranslation?.product_description || "",
    };
};

const currency = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "UAH",
});

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
                    {(["dashboard", "products", "orders", "users"] as AdminView[]).map((view) => (
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
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(true);

    const loadSummary = useCallback(async () => {
        setIsLoading(true);
        setError("");
        try {
            setSummary(await fetchAdminSummary());
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
          ]
        : [];

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
            {!isLoading && !error && (
                <div className={styles.metricGrid}>
                    {cards.map(([label, value]) => (
                        <article key={label} className={styles.metric}>
                            <span>{label}</span>
                            <strong>{value}</strong>
                        </article>
                    ))}
                </div>
            )}
        </section>
    );
};

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
    const [form, setForm] = useState<ProductFormState>(emptyProductForm);
    const [editingProductId, setEditingProductId] = useState<string | null>(null);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);

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

    const resetForm = () => {
        setEditingProductId(null);
        setForm(emptyProductForm());
    };

    const editProduct = async (productId: string) => {
        setError("");
        try {
            const product = await fetchProduct(productId);
            setEditingProductId(productId);
            setForm(productToForm(product));
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to load product."));
        }
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
                    <div className={styles.formGrid}>
                        <label>
                            English name
                            <input
                                value={form.en_name}
                                onChange={(event) => setForm({...form, en_name: event.target.value})}
                                required
                            />
                        </label>
                        <label>
                            Ukrainian name
                            <input
                                value={form.ukr_name}
                                onChange={(event) => setForm({...form, ukr_name: event.target.value})}
                                required
                            />
                        </label>
                        <label>
                            English description
                            <textarea
                                value={form.en_description}
                                onChange={(event) => setForm({...form, en_description: event.target.value})}
                                required
                            />
                        </label>
                        <label>
                            Ukrainian description
                            <textarea
                                value={form.ukr_description}
                                onChange={(event) => setForm({...form, ukr_description: event.target.value})}
                                required
                            />
                        </label>
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
                            Stock
                            <input
                                type="number"
                                min="0"
                                value={form.stock_quantity}
                                onChange={(event) => setForm({...form, stock_quantity: event.target.value})}
                                required
                            />
                        </label>
                        <label>
                            Category
                            <select
                                value={form.category}
                                onChange={(event) => setForm({...form, category: event.target.value})}
                            >
                                <option value="Chebureks">Chebureks</option>
                                <option value="Pies">Pies</option>
                                <option value="Drinks">Drinks</option>
                                <option value="Other">Other</option>
                            </select>
                        </label>
                        <label>
                            Image URL
                            <input
                                value={form.image_src}
                                onChange={(event) => setForm({...form, image_src: event.target.value})}
                                required
                            />
                        </label>
                    </div>
                    <div className={styles.formActions}>
                        <button type="submit" className={styles.primaryButton} disabled={isSaving}>
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
                            headers={["Product", "Category", "Price", "Stock", "Actions"]}
                            rows={products.map((product) => [
                                <strong>{product.name}</strong>,
                                product.category,
                                currency.format(product.price),
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
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [isLoading, setIsLoading] = useState(true);

    const selectedOrder = useMemo(
        () => orders.find((order) => order.order_id === selectedOrderId) || orders[0],
        [orders, selectedOrderId],
    );

    const loadOrders = useCallback(async () => {
        setIsLoading(true);
        setError("");
        try {
            const nextOrders = await fetchOrders();
            setOrders(nextOrders);
            setSelectedOrderId((previousId) => previousId || nextOrders[0]?.order_id || null);
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to load orders."));
        } finally {
            setIsLoading(false);
        }
    }, []);

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
                                order.status,
                                currency.format(order.total_price || 0),
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
                            <label>
                                Status
                                <select
                                    value={selectedOrder.status}
                                    onChange={(event) =>
                                        void changeStatus(
                                            selectedOrder.order_id,
                                            event.target.value as OrderStatus,
                                        )
                                    }
                                >
                                    {ORDER_STATUSES.map((status) => (
                                        <option key={status} value={status}>
                                            {status}
                                        </option>
                                    ))}
                                </select>
                            </label>
                            <div className={styles.orderAddress}>
                                <strong>Delivery</strong>
                                <span>
                                    {selectedOrder.address.street_number} {selectedOrder.address.street_name},{" "}
                                    {selectedOrder.address.city}, {selectedOrder.address.state}
                                </span>
                            </div>
                            <div className={styles.orderItems}>
                                {selectedOrder.products.map((product) => (
                                    <div key={`${selectedOrder.order_id}-${product.name}`} className={styles.orderItem}>
                                        <span>{product.name}</span>
                                        <span>
                                            {product.quantity} x {currency.format(product.price)}
                                        </span>
                                    </div>
                                ))}
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
            setUsers(await fetchUsers());
        } catch (requestError) {
            setError(getAdminErrorMessage(requestError, "Unable to load users."));
        } finally {
            setIsLoading(false);
        }
    }, []);

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
