import React from 'react';

const Header = () => {
  return (
    <header className='header'>
      <div className='header-content'>
        <h1>Dental Practice</h1>
        <nav>
          <ul>
            <li><a href='#'>Home</a></li>
            <li><a href='#'>About Us</a></li>
            <li><a href='#'>Services</a></li>
            <li><a href='#'>Contact</a></li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

const Footer = () => {
  return (
    <footer className='footer'>
      <div className='footer-content'>
        <p>&copy; 2023 Dental Practice. All rights reserved.</p>
        <ul>
          <li><a href='#'>Privacy Policy</a></li>
          <li><a href='#'>Terms of Service</a></li>
        </ul>
      </div>
    </footer>
  );
};

const HeaderFooter = () => {
  return (
    <>
      <Header />
      <Footer />
    </>
  );
};

export default HeaderFooter;