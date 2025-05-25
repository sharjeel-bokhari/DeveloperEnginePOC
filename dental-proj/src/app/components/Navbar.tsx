"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import React from 'react';

const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/about', label: 'About Us' }
];

const Navbar: React.FC = () => {
  const pathname = usePathname();
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <span className="navbar-logo">🦷 SmileBright</span>
        <ul className="navbar-links">
          {navLinks.map(link => (
            <li key={link.href}>
              <Link href={link.href} legacyBehavior>
                <a className={pathname === link.href ? 'active' : ''}>{link.label}</a>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
