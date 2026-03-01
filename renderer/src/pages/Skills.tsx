import React, { useState, useEffect } from 'react';
import { Plus, ToggleLeft, ToggleRight, Trash2, Play } from 'lucide-react';

interface Skill {
  id: number;
  name: string;
  category: string;
  description: string;
  is_active: boolean;
}

export function Skills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSkills();
  }, []);

  const fetchSkills = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/skills');
      const data = await res.json();
      setSkills(data);
    } catch (error) {
      console.error('Failed to fetch skills:', error);
    }
    setLoading(false);
  };

  const handleToggle = async (skill: Skill) => {
    const endpoint = skill.is_active 
      ? `/api/v1/skills/${skill.id}/deactivate`
      : `/api/v1/skills/${skill.id}/activate`;
    
    try {
      await fetch(`http://localhost:8000${endpoint}`, { method: 'POST' });
      fetchSkills();
    } catch (error) {
      console.error('Failed to toggle skill:', error);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await fetch(`http://localhost:8000/api/v1/skills/${id}`, { method: 'DELETE' });
      fetchSkills();
    } catch (error) {
      console.error('Failed to delete skill:', error);
    }
  };

  const handleLoadFromFilesystem = async () => {
    try {
      await fetch('http://localhost:8000/api/v1/skills/load-from-filesystem', { method: 'POST' });
      fetchSkills();
    } catch (error) {
      console.error('Failed to load skills:', error);
    }
  };

  return (
    <div className="skills-page">
      <div className="page-header">
        <h1>Skills</h1>
        <p>Manage automation skills for your agents</p>
      </div>

      <div className="page-actions">
        <button className="btn-secondary" onClick={handleLoadFromFilesystem}>
          Load from Filesystem
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading skills...</div>
      ) : skills.length === 0 ? (
        <div className="empty-state">
          <p>No skills found. Add skills to enable automation.</p>
        </div>
      ) : (
        <div className="skills-grid">
          {skills.map(skill => (
            <div key={skill.id} className={`skill-card ${skill.is_active ? 'active' : ''}`}>
              <div className="skill-header">
                <h3>{skill.name}</h3>
                <button 
                  className="toggle-btn"
                  onClick={() => handleToggle(skill)}
                >
                  {skill.is_active ? <ToggleRight /> : <ToggleLeft />}
                </button>
              </div>
              <span className="skill-category">{skill.category}</span>
              <p className="skill-description">{skill.description}</p>
              <div className="skill-actions">
                <button className="btn-icon"><Play size={16} /></button>
                <button className="btn-icon danger" onClick={() => handleDelete(skill.id)}>
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
