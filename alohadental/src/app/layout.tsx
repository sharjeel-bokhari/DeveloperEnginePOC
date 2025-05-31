import './globals.css';
import type { Metadata } from 'next';
import React from 'react';
import ClientThemeProvider from './components/ClientThemeProvider';

export const metadata: Metadata = {
  title: 'Aloha Dental',
  description: 'Aloha Dental - Your Family Dentist',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900">
        <ClientThemeProvider>{children}</ClientThemeProvider>
      </body>
    </html>
  );
}
