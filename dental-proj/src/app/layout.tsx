import './globals.css';
import React from 'react';
import Navbar from './components/Navbar';

export const metadata = {
  title: 'SmileBright Dental',
  description: 'Modern dental practice landing page',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
