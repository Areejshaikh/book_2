import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import QdrantSearch from './QdrantSearch';

describe('QdrantSearch Component', () => {
  let originalFetch;

  beforeAll(() => {
    originalFetch = global.fetch;
    global.fetch = jest.fn();
  });

  afterAll(() => {
    global.fetch = originalFetch;
  });

  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders search input and button', () => {
    render(<QdrantSearch />);

    expect(
      screen.getByPlaceholderText('Enter your search query...')
    ).toBeInTheDocument();

    expect(
      screen.getByRole('button', { name: /search/i })
    ).toBeInTheDocument();
  });

  test('updates input value on change', () => {
    render(<QdrantSearch />);

    const input = screen.getByPlaceholderText('Enter your search query...');
    fireEvent.change(input, { target: { value: 'test query' } });

    expect(input.value).toBe('test query');
  });

  test('submits search query and displays results', async () => {
    const mockResults = [
      {
        content: 'Test content snippet',
        source: 'https://example.com/test',
        score: 0.92,
      },
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ results: mockResults }),
    });

    render(<QdrantSearch />);

    fireEvent.change(
      screen.getByPlaceholderText('Enter your search query...'),
      { target: { value: 'test query' } }
    );

    fireEvent.click(
      screen.getByRole('button', { name: /search/i })
    );

    await waitFor(() => {
      expect(
        screen.getByText('Test content snippet')
      ).toBeInTheDocument();
    });
  });

  test('shows error message when API call fails', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));

    render(<QdrantSearch />);

    fireEvent.change(
      screen.getByPlaceholderText('Enter your search query...'),
      { target: { value: 'test query' } }
    );

    fireEvent.click(
      screen.getByRole('button', { name: /search/i })
    );

    await waitFor(() => {
      expect(
        screen.getByText(/failed to retrieve results/i)
      ).toBeInTheDocument();
    });
  });
});
