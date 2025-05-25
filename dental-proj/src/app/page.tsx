"use client";
import React from "react";
import HeroSection from "./components/HeroSection";
import ServicesSection from "./components/ServicesSection";
import ContactForm from "./components/ContactForm";

export default function Home() {
  return (
    <main className="main-container">
      <HeroSection />
      <ServicesSection />
      <ContactForm />
    </main>
  );
}
