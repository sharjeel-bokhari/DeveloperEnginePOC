import React from 'react';

const services = [
  { title: 'Teeth Whitening', desc: 'Brighten your smile with our advanced whitening treatments.' },
  { title: 'Dental Implants', desc: 'Restore missing teeth with natural-looking dental implants.' },
  { title: 'Routine Checkups', desc: 'Maintain oral health with regular exams and cleanings.' },
];

const ServicesSection: React.FC = () => (
  <section className="services-section">
    <h2>Our Services</h2>
    <div className="services-list">
      {services.map((service, idx) => (
        <div className="service-card" key={idx}>
          <h3>{service.title}</h3>
          <p>{service.desc}</p>
        </div>
      ))}
    </div>
  </section>
);

export default ServicesSection;
