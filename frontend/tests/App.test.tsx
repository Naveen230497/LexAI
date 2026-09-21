import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../src/App';
import { expect, test, describe } from 'vitest';

describe('LexAI Frontend', () => {
  test('renders the main landing page', () => {
    render(<App />);
    const heading = screen.getByText(/Decode contracts in seconds/i);
    expect(heading).toBeInTheDocument();
  });
});
