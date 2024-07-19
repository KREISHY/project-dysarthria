//Компонент объекта теста для списков на страницах Tests, MyTests 
import React from 'react';
import './style.css';

const Test = ({ name, description }) => {
  return (
    <div className="test-item">
      <div className="test-header">
        <h3 className="test-title">{name}</h3>
        <p className="test-description">{description}</p>
      </div>
    </div>
  );
};

export default Test;