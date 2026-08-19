import AsyncStorage from '@react-native-async-storage/async-storage';
import React, { createContext, ReactNode, useContext, useEffect, useMemo, useState } from 'react';
import type { Product } from '@/data/catalog';
export interface CartItem { product: Product; quantity: number; }
export interface ShopUser { name: string; email: string; }
export interface Order { id: string; createdAt: string; status: 'Processing' | 'Shipped' | 'Delivered'; items: CartItem[]; subtotal: number; shipping: number; total: number; address: string; }
interface PersistedShop { user: ShopUser | null; cart: CartItem[]; orders: Order[]; }
interface ShopContextValue { user: ShopUser | null; cart: CartItem[]; orders: Order[]; hydrated: boolean; cartCount: number; cartTotal: number; signIn: (user: ShopUser) => void; signOut: () => void; addToCart: (product: Product) => void; updateQuantity: (productId: string, quantity: number) => void; removeFromCart: (productId: string) => void; placeOrder: (address: string) => Order | null; }
const STORAGE_KEY = '@shoptrail/state';
const ShopContext = createContext<ShopContextValue | null>(null);
export function ShopProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<ShopUser | null>(null); const [cart, setCart] = useState<CartItem[]>([]); const [orders, setOrders] = useState<Order[]>([]); const [hydrated, setHydrated] = useState(false);
  useEffect(() => { AsyncStorage.getItem(STORAGE_KEY).then((value) => { if (!value) return; const saved = JSON.parse(value) as PersistedShop; setUser(saved.user ?? null); setCart(saved.cart ?? []); setOrders(saved.orders ?? []); }).catch(() => undefined).finally(() => setHydrated(true)); }, []);
  useEffect(() => { if (!hydrated) return; AsyncStorage.setItem(STORAGE_KEY, JSON.stringify({ user, cart, orders } satisfies PersistedShop)).catch(() => undefined); }, [cart, hydrated, orders, user]);
  const signIn = (nextUser: ShopUser) => setUser(nextUser); const signOut = () => setUser(null);
  const addToCart = (product: Product) => setCart((current) => { const existing = current.find((item) => item.product.id === product.id); if (existing) return current.map((item) => item.product.id === product.id ? { ...item, quantity: item.quantity + 1 } : item); return [...current, { product, quantity: 1 }]; });
  const updateQuantity = (productId: string, quantity: number) => { if (quantity <= 0) { setCart((current) => current.filter((item) => item.product.id !== productId)); return; } setCart((current) => current.map((item) => item.product.id === productId ? { ...item, quantity } : item)); };
  const removeFromCart = (productId: string) => setCart((current) => current.filter((item) => item.product.id !== productId));
  const placeOrder = (address: string) => { if (!cart.length) return null; const subtotal = cart.reduce((sum, item) => sum + item.product.price * item.quantity, 0); const shipping = subtotal >= 100 ? 0 : 8; const order: Order = { id: 'ST-' + Date.now().toString().slice(-6), createdAt: new Date().toISOString(), status: 'Processing', items: cart, subtotal, shipping, total: subtotal + shipping, address }; setOrders((current) => [order, ...current]); setCart([]); return order; };
  const value = useMemo(() => ({ user, cart, orders, hydrated, cartCount: cart.reduce((sum, item) => sum + item.quantity, 0), cartTotal: cart.reduce((sum, item) => sum + item.product.price * item.quantity, 0), signIn, signOut, addToCart, updateQuantity, removeFromCart, placeOrder }), [cart, hydrated, orders, user]);
  return <ShopContext.Provider value={value}>{children}</ShopContext.Provider>;
}
export function useShop() { const context = useContext(ShopContext); if (!context) throw new Error('useShop must be used within ShopProvider'); return context; }
