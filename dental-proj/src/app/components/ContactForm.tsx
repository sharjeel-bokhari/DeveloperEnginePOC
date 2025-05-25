import React from 'react';

const ContactForm: React.FC = () => (
  <section className="contact-section" id="contact">
    <h2>Contact Us</h2>
    <form className="contact-form">
      <input type="text" name="name" placeholder="Your Name" required />
      <input type="email" name="email" placeholder="Your Email" required />
      <textarea name="message" placeholder="Your Message" rows={4} required></textarea>
      <button type="submit">Send Message</button>
    </form>
  </section>
);

export default ContactForm;
