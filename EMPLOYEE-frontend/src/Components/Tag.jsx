import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Tag() {
  const [inputValue, setInputValue] = useState('');
  const [tags, setTags] = useState([]);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    // Fetch tags from Flask backend when component mounts
    axios.get('http://localhost:5000/api/tag_list')
      .then(response => {
        setTags(response.data.tags);
      })
      .catch(error => {
        setError(error.message);
      });
  }, []);

  const handleChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() !== '') {
      // Send the new tag to Flask backend
      axios.post('http://localhost:5000/api/add_tag', { tag: inputValue })
        .then(response => {
          if (response.data.message) {
            // Add the new tag to the local state
            setTags([...tags, { id: tags.length + 1, tag: inputValue }]);
            setInputValue('');
            setError(null);
            setSuccessMessage('Tag added successfully!');
          } else {
            setError(response.data.error);
          }
        })
        .catch(error => {
          setError(error.message);
        });
    }
  };

  return (
    <div className="container">
      <p style={{ fontSize: '40px' }}>Tags</p>
      {error && <p>Error: {error}</p>}
      {successMessage && <p className="text-success">{successMessage}</p>}
      <form onSubmit={handleSubmit}>
        <div className="row">
          <div className="col-auto">
            <label htmlFor="inputTag" className="visually-hidden">Tag</label>
            <input
              type="text"
              className="form-control mb-3"
              id="inputTag"
              placeholder="Add new tag"
              value={inputValue}
              onChange={handleChange}
            />
          </div>
          <div className="col-auto">
            <button type="submit" className="btn btn-primary mb-3">Add Tag</button>
          </div>
        </div>
      </form>
      <table className="table mt-3 table">
        <thead>
          <tr>
            <th>#</th>
            <th>Tag</th>
          </tr>
        </thead>
        <tbody>
          {tags.map((tag, index) => (
            <tr key={index}>
              <td>{tag.id}</td>
              <td>{tag.tag}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Tag;
