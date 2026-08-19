import type { ImageSourcePropType } from 'react-native';

export type Category = 'All' | 'Home' | 'Workspace' | 'Kitchen' | 'Wellness';
export interface Product { id: string; name: string; category: Exclude<Category, 'All'>; price: number; compareAt?: number; description: string; details: string[]; image: ImageSourcePropType; accent: string; rating: number; reviews: number; badge?: string; }
export const categories: { label: Category; icon: string }[] = [
  { label: 'All', icon: 'sparkles' }, { label: 'Home', icon: 'home' }, { label: 'Workspace', icon: 'briefcase' }, { label: 'Kitchen', icon: 'coffee' }, { label: 'Wellness', icon: 'sun' },
];
export const products: Product[] = [
  { id: 'forma-carafe', name: 'Forma Carafe', category: 'Kitchen', price: 58, compareAt: 72, description: 'A quiet centerpiece for slow mornings and shared tables.', details: ['Hand-finished ceramic', '1.2L capacity', 'Dishwasher safe'], image: require('../assets/images/carafe.jpg'), accent: '#D9C8B4', rating: 4.9, reviews: 128, badge: 'Best seller' },
  { id: 'dune-throw', name: 'Dune Throw', category: 'Home', price: 84, description: 'Soft woven cotton with a little weight and a lot of warmth.', details: ['100% woven cotton', '130 x 180 cm', 'Machine washable'], image: require('../assets/images/throw.jpg'), accent: '#D66B4D', rating: 4.8, reviews: 84, badge: 'New in' },
  { id: 'halo-lamp', name: 'Halo Desk Lamp', category: 'Workspace', price: 112, compareAt: 138, description: 'A warm pool of light for the work that deserves your focus.', details: ['Brushed brass finish', 'Opal glass shade', 'Warm LED bulb included'], image: require('../assets/images/lamp.jpg'), accent: '#BDAA74', rating: 4.7, reviews: 61, badge: 'Limited' },
  { id: 'arc-tray', name: 'Arc Catchall', category: 'Home', price: 42, description: 'A small landing place for keys, rings, and daily rituals.', details: ['Powder-coated steel', 'Felt base', 'Designed in Toronto'], image: require('../assets/images/lamp.jpg'), accent: '#8EA5A0', rating: 4.6, reviews: 39 },
  { id: 'mori-mug', name: 'Mori Mug Set', category: 'Kitchen', price: 36, description: 'Two imperfectly perfect cups for your everyday pour.', details: ['Set of 2', 'Stoneware ceramic', 'Microwave safe'], image: require('../assets/images/carafe.jpg'), accent: '#B98C7E', rating: 4.9, reviews: 105 },
  { id: 'still-kit', name: 'Still Ritual Kit', category: 'Wellness', price: 64, description: 'A small collection for making space between one thing and the next.', details: ['Soy candle', 'Botanical bath soak', 'Linen eye pillow'], image: require('../assets/images/throw.jpg'), accent: '#C7B6A4', rating: 4.8, reviews: 47 },
];
export function getProduct(id: string) { return products.find((product) => product.id === id); }
