"use client";
import React, { useRef, useState, useEffect } from "react";

type FadeInSectionProps = {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
};

const FadeInSection: React.FC<FadeInSectionProps> = ({ children, className = "", style = {} }) => {
  const domRef = useRef<HTMLDivElement>(null);
  const [isVisible, setVisible] = useState(false);

  useEffect(() => {
    const { current } = domRef;
    if (!current) return;
    const observer = new window.IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setVisible(true);
            observer.disconnect(); // Animate only once
          }
        });
      },
      { threshold: 0.15 }
    );
    observer.observe(current);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={domRef}
      className={`fade-in-section${isVisible ? " is-visible" : ""} ${className}`.trim()}
      style={style}
    >
      {children}
    </div>
  );
};

export default FadeInSection;
