import React from 'react';
import FadeInSection from '../components/FadeInSection';

export default function AboutPage() {
  return (
    <section className="about-section">
      <FadeInSection>
        <h1>About Us</h1>
      </FadeInSection>
      <FadeInSection>
        <p>
          SmileBright Dental is dedicated to providing exceptional dental care with a modern touch. Our experienced team ensures every patient feels comfortable and confident in their smile. We use the latest technology and techniques in a warm, welcoming environment.
        </p>
      </FadeInSection>
      <FadeInSection>
        <p>
          Whether you need routine checkups, cosmetic treatments, or restorative procedures, we are here to help you achieve optimal oral health and a smile you love.
        </p>
      </FadeInSection>
      <FadeInSection>
        <div className="about-context">
          <h2>Our Philosophy</h2>
          <p>
            At SmileBright, we believe dental care should be comfortable, transparent, and tailored to your needs. Our staff takes the time to educate you about your oral health and treatment options, ensuring you make informed decisions every step of the way.
          </p>
        </div>
      </FadeInSection>
      <FadeInSection>
        <div className="about-context">
          <h2>Why Choose Us?</h2>
          <ul>
            <li>Experienced, compassionate dental professionals</li>
            <li>State-of-the-art technology and techniques</li>
            <li>Personalized, patient-centered care</li>
            <li>Comfortable, modern environment</li>
          </ul>
        </div>
      </FadeInSection>
    </section>
  );
}
