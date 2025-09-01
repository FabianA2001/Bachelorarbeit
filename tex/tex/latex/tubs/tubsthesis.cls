%%
%% This is file `tubsthesis.cls',
%% generated with the docstrip utility.
%%
%% The original source files were:
%%
%% ../tubsvers.inc  (with options: `default,extra')
%% tubsthesis.dtx  (with options: `head,option,execoption,command,environment')
%% 
%% This is a generated file.
%% 
%% Copyright (C) 2020 by Philip Hönnecke
%% 
%% This file may be distributed and/or modified under the
%% conditions of the LaTeX Project Public License, either
%% version 1.2 of this license or (at your option) any later
%% version. The latest version of this license is in:
%% 
%%   http://www.latex-project.org/lppl.txt
%% 
%% and version 1.2 or later is part of all distributions of
%% LaTeX version 1999/12/01 or later.
%% 
\RequirePackage{ifthen}
\RequirePackage{scrlfile}%TODO: KOMA-Check?
\RequirePackage{etoolbox}%
\begingroup
  \makeatletter
  \ifx\tubslatexVersion\undefined
    \newcommand*{\check@tubslatexVersion}[1]{%
      \gdef\tubslatexVersion{#1}%
    }%
  \else
    \newcommand*{\check@tubslatexVersion}[1]{%
      \def\@tempa{#1}%
      \ifx\tubslatexVersion\@tempa\else
        \@latex@warning@no@line{%
          \noexpand\tubslatexVersion\space is
          `\tubslatexVersion',\MessageBreak
          but `#1' was expected!\MessageBreak
          You should not use classes, packages or files
          from\MessageBreak
          different tubslatex versions%
        }%
      \fi
    }
  \fi
  \check@tubslatexVersion{2024/02/22 v1.3.5-r140 tubslatex}%
\endgroup
\providecommand{\tubslatex}{tubs\LaTeX}
\AfterPackage*{ucs}{%
  \pretocmd{\author}{\PrerenderUnicode{ä,ö,ü,ß}}{}{}%
  \pretocmd{\title}{\PrerenderUnicode{ä,ö,ü,ß}}{}{}%
}
\AtBeginDocument{
  \@ifpackageloaded{hyperref}{%
    \@ifundefined{inputencodingname}{}{%
      \hypersetup{
        pdftitle = {\@title},
        pdfauthor = {\@author},
        pdfcreator = {\tubslatexVersion}
      }
    }
  }{}
}
\NeedsTeXFormat{LaTeX2e}[1999/12/01]
\ProvidesClass{tubsthesis}[\tubslatexVersion tubs thesis class]
\LoadClass[%
a4paper,              % DIN A4
twoside,              % doublesided document
cmyk,                 % use CMYK colors
bcor=15mm,            % extra space for book binding
bibliography=totoc,   % bibliography gets unnumbered entry
nexus,                % corporate design font
lnum,                 % use "Versalziffern" instead of
                      % "Mediaevalziffern"
extramargin,          % override corporate design margin
                      % to give more space for one-column text
]{%
tubsbook%
}
\RequirePackage{xkeyval}
\usepackage{csquotes}
\usepackage[backend=biber]{biblatex}
\PassOptionsToPackage{hyphens}{url}
\usepackage[hidelinks]{hyperref}
\usepackage{xparse} % for \NewDocumentCommand only
\usepackage{pdfpages} % for including proposal in thesis
\define@boolkey{%
tubsthesis.cls%
}[cls]{german}[true]{}
\define@boolkey{%
tubsthesis.cls%
}[cls]{english}[true]{%
    \setkeys{tubsthesis.cls}{german=false}
}
\define@boolkey{%
tubsthesis.cls%
}[cls]{proposal}[true]{}
\define@boolkey{%
tubsthesis.cls%
}[cls]{nolistoffigures}[true]{}
\define@boolkey{%
tubsthesis.cls%
}[cls]{nolistoftables}[true]{}
\define@boolkey{%
tubsthesis.cls%
}[cls]{noabstract}[true]{}
\define@boolkey{%
tubsthesis.cls%
}[cls]{noappendix}[true]{}
\define@boolkey{%
tubsthesis.cls%
}[cls]{nodate}[true]{}
\newcommand{\thesistype}{default}
\newif\iftubsthesis@diss
\tubsthesis@dissfalse
\newif\iftubsthesis@customtype
\tubsthesis@customtypefalse
\DeclareOptionX{thesistype}{
    \def\temp{#1}
    \def\bachelor{bachelor}
    \def\master{master}
    \def\project{project}
    \def\diss{dissertation}
    \ifclsgerman % begin german
        \ifx\temp\bachelor
            \def\thesistype{Bachelorarbeit}
        \else
            \ifx\temp\master
                \def\thesistype{Masterarbeit}
            \else
                \ifx\temp\project
                    \def\thesistype{Projektarbeit}
                \else
                    \ifx\temp\diss
                        \def\thesistype{Dissertation}
                        \unless\ifclsproposal
                            \tubsthesis@disstrue
                            \subtitle{Research Proposal}
                        \fi
                    \else
                        % unknown type
                        \def\thesistype{#1}
                        \tubsthesis@customtypetrue
                    \fi
                \fi
            \fi
        \fi
    \else % end german / begin english
        \ifx\temp\bachelor
            \def\thesistype{Bachelor's Thesis}
        \else
            \ifx\temp\master
                \def\thesistype{Master's Thesis}
            \else
                \ifx\temp\project
                    \def\thesistype{Project Thesis}
                \else
                    \ifx\temp\diss
                        \def\thesistype{Dissertation}
                        \unless\ifclsproposal
                            \tubsthesis@disstrue
                            \subtitle{Research Proposal}
                        \fi
                    \else
                        % unknown type
                        \def\thesistype{#1}
                        \tubsthesis@customtypetrue
                    \fi
                \fi
            \fi
        \fi
    \fi % end english
}
\ExecuteOptionsX{
    german=false,
    nolistoffigures=false,
    nolistoftables=false,
    noabstract=false,
    noappendix=false,
    nodate=false,
    thesistype=bachelor}
\ProcessOptionsX*\relax
\ifclsgerman
    % english is main language, german is alternative
    \usepackage[english,ngerman]{babel}
\else
    % german is main language, english is alternative
    \usepackage[ngerman,english]{babel}
\fi
\usepackage[useregional]{datetime2}
\ifclsproposal
    \usepackage{tabularx}
\fi
\newcommand{\name}{%
    \ClassWarningNoLine{tubsthesis}{%
        No name set.\MessageBreak
        Use \protect\thesisname\space to set it
    }
}
\newcommand{\thesisname}[1]{%
    \author{#1}
    \renewcommand{\name}{#1}
}
\newcommand{\thesistypeoverwrite}[1]{%
    \def\thesistype{#1}
    \tubsthesis@customtypetrue
}
\newcommand{\thesissupervisors}[3]{%
\newcounter{SupervisorsCounter}
\def\temp{#1}\ifx\temp\empty
        \newcommand{\supervisorone}{}
\newcommand{\supervisoronesign}{}
\else
\newcommand{\supervisorone}{#1\\}
\newcommand{\supervisoronesign}{%
        #1           & \rule[-0.5ex]{\linewidth}{1pt}
        \newline\itshape(\signature)\\[5ex]
}
\stepcounter{SupervisorsCounter}
\fi

\def\temp{#2}\ifx\temp\empty
\newcommand{\supervisortwo}{}
\newcommand{\supervisortwosign}{}
\else
\newcommand{\supervisortwo}{#2\\}
\newcommand{\supervisortwosign}{%
        #2           & \rule[-0.5ex]{\linewidth}{1pt}
        \newline\itshape(\signature)\\[5ex]
}
\stepcounter{SupervisorsCounter}
\fi

\def\temp{#3}\ifx\temp\empty
\newcommand{\supervisorthree}{}
\newcommand{\supervisorthreesign}{}
\else
\newcommand{\supervisorthree}{#3\\}
\newcommand{\supervisorthreesign}{%
        #3           & \rule[-0.5ex]{\linewidth}{1pt}
        \newline\itshape(\signature)\\[5ex]
}
\stepcounter{SupervisorsCounter}
\fi

\ifnum\theSupervisorsCounter=1
\newcommand{\supervisorstring}{Supervisor:}
\else
\newcommand{\supervisorstring}{Supervisors:}
\fi
}
\newcommand{\tubsthesis@professor}{%
    \ClassWarningNoLine{tubsthesis}{%
        No professor set.\MessageBreak
        Use \protect\thesisprofessor\space to set one
    }
}
\newcommand{\tubsthesis@professortwo}{%
    \ClassWarningNoLine{tubsthesis}{%
        No second professor set.\MessageBreak
        Use \protect\thesisprofessor\space to set one
    }
}
\newcommand{\thesisprofessor}[2][]{%
    \renewcommand{\tubsthesis@professor}{#2}
    \ifthenelse{\equal{#1}{}}{%
        % No second professor given
    }{%
        \renewcommand{\tubsthesis@professortwo}{#1}
    }
}
\newcommand{\titleenglish}{%
    \ClassWarningNoLine{tubsthesis}{%
        No thesis title set.\MessageBreak
        Use \protect\thesistitle\space to set one
    }
}
\newcommand{\titlegerman}{%
    \ClassWarningNoLine{tubsthesis}{%
        No thesis title set.\MessageBreak
        Use \protect\thesistitle\space to set one
    }
}
\newif\ifextratitle\extratitlefalse
\newcommand{\thesistitle}[2]{%
    \ifclsgerman % begin german
        \title{#1}
        \def\temp{#2}
    \else % end german / begin english
        \title{#2}
        \def\temp{#1}
    \fi % end english
    \unless\ifx\temp\empty
        \extratitletrue
    \fi
    \renewcommand{\titlegerman}{#1}
    \renewcommand{\titleenglish}{#2}
}
\DTMsavedate{tubsthesis@begindate}{2000-01-01}
\newcommand{\thesisbegindate}[1]{%
    \DTMsavedate{tubsthesis@begindate}{#1}
}
\newcommand{\tubsthesis@date}{%
    \DTMifsaveddate{tubsthesis@date}{%
        \DTMusedate{tubsthesis@date}
    }{%
        \DTMtoday
    }
}
\newcommand{\thesisenddate}[1]{%
    \DTMsavedate{tubsthesis@date}{#1}
}
\newcommand{\tubsthesis@institute}{%
    \ClassWarningNoLine{tubsthesis}{%
        No institute name set.\MessageBreak
        Use \protect\thesisinstitute\space to set it
    }
}
\newcommand{\tubsthesis@institutelogo}{%
    \tubsthesis@institute
}
\newcommand{\thesisinstitute}[2][]{%
    \renewcommand{\tubsthesis@institute}{#2}
    \def\temp{#1}
    \unless\ifx\temp\empty % No logo given
        \renewcommand{\tubsthesis@institutelogo}{#1}
    \fi
}
\newif\ifextraabstract\extraabstractfalse
\newcommand{\mainabstract}{%
    \ClassWarningNoLine{tubsthesis}{%
        No abstract set.\MessageBreak
        Use \protect\thesisabstract\space to set one
    }
}
\NewDocumentCommand{\thesisabstract}{ O{} m }{%
    \def\temp{#1}
    \unless\ifx\temp\empty % begin extra abstract set
        \extraabstracttrue
        \newcommand{\extraabstract}{#1}
    \fi % end extra abstract set
    \renewcommand{\mainabstract}{#2}
}
\newcommand{\tubsthesis@posttitlecontent}{}
\newcommand{\thesisposttitle}[1]{%
    \renewcommand{\tubsthesis@posttitlecontent}{#1}
}
\newif\ifincludedproposal
\includedproposalfalse
\newcommand{\tubsthesis@includedproposal}{}
\newcommand{\thesisincludedproposal}[1]{%
    \renewcommand{\tubsthesis@includedproposal}{%
        \includepdf[pages=-]{#1}
        \cleardoublepage
    }
    \includedproposaltrue
}
\newcommand{\matrikelnummer}{%
    \ClassWarningNoLine{tubsthesis}{%
        No identification number (Matrikelnummer) set.\MessageBreak
        Use \protect\thesismatrikel\space to set it
    }
}
\newcommand{\thesismatrikel}[1]{%
    \renewcommand{\matrikelnummer}{#1}
}
\newcommand{\mail}{%
    \ClassWarningNoLine{tubsthesis}{%
        No email address set.\MessageBreak
        Use \protect\thesisemail\space to set it
    }
}
\newcommand{\thesisemail}[1]{%
    \renewcommand{\mail}{#1}
}
\newcommand{\studysubject}{%
    \ClassWarningNoLine{tubsthesis}{%
        No thesis major set.\MessageBreak
        Use \protect\thesismajor\space to set it
    }
}
\newcommand{\thesismajor}[1]{%
    \renewcommand{\studysubject}{#1}
    % TODO: Maybe change this too (to major)
}
\newcommand{\duration}{%
    \ClassWarningNoLine{tubsthesis}{%
        No thesis duration set.\MessageBreak
        Use \protect\thesisduration\space to set it
    }
}
\newcommand{\thesisduration}[1]{%
    \renewcommand{\duration}{#1}
}
\newif\iftubsthesis@presentationpoints
\tubsthesis@presentationpointsfalse
\newcommand{\presentationpoints}{}
\newcommand{\thesispresentationpoints}[1]{%
    \tubsthesis@presentationpointstrue
    \renewcommand{\presentationpoints}{#1}
}
\newif\iftubsthesis@finalprint
\tubsthesis@finalprintfalse
\newcommand{\thesisfinalprint}{%
    \tubsthesis@finalprinttrue
}
\DTMsavedate{tubsthesis@birthdate}{2500-12-20}
\newcommand{\thesisbirthdate}[1]{%
    \DTMsavedate{tubsthesis@birthdate}{#1}
}
\newcommand{\tubsthesis@birthplace}{%
    \ClassWarningNoLine{tubsthesis}{%
        No birthplace was set.\MessageBreak
        Use \protect\thesisbirthplace\space to set one
    }
}
\newcommand{\thesisbirthplace}[1]{%
    \renewcommand{\tubsthesis@birthplace}{#1}
}
\DTMsavedate{tubsthesis@disputationdate}{2020-01-05}
\newcommand{\thesisdisputationdate}[1]{%
    \DTMsavedate{tubsthesis@disputationdate}{#1}
}
\newcommand{\tubsthesis@faculty}{%
    \ClassWarningNoLine{tubsthesis}{%
        No faculty was set.\MessageBreak
        Use \protect\thesisfaculty\space to set one
    }
}
\newcommand{\thesisfaculty}[1]{%
    \renewcommand{\tubsthesis@faculty}{#1}
}
\newcommand{\tubsthesis@degree}{%
    \ClassWarningNoLine{tubsthesis}{%
        No degree was set.\MessageBreak
        Use \protect\thesisdegree\space to set one
    }
}
\newcommand{\tubsthesis@degreearticle}{eines}
\newcommand{\thesisdegree}[2][]{%
    \renewcommand{\tubsthesis@degree}{#2}
    \ifthenelse{\equal{#1}{}}{}{\renewcommand{\tubsthesis@degreearticle}{#1}}
}
\newcommand{\tubsthesis@printyear}{%
    \DTMfetchyear{tubsthesis@disputationdate}
}
\newcommand{\thesisprintyear}[1]{%
    \renewcommand{\tubsthesis@printyear}{#1}
}
\newif\iftubsthesis@cumulative
\tubsthesis@cumulativefalse
\newcommand{\thesiscumulative}{%
    \tubsthesis@cumulativetrue
}
\ifclsgerman
    \newcommand{\signature}{Datum, Unterschrift}
\else
    \newcommand{\signature}{Date, Signature}
\fi
\newlength\tubsthesis@tablewidth
\setlength\tubsthesis@tablewidth{.7\textwidth}
\newenvironment{thesis}{%

\ifclsproposal % begin proposal
    % chapter command overwrite
    % to avoid cleardoublepage before new chapters
    \ifthenelse{\isundefined{\RedeclareSectionCommand}}{%
    }{%
        \RedeclareSectionCommand[style=section,indent=0pt]{chapter}
    }
\fi % end proposal

\ifclsproposal % begin proposal
    \ifclsgerman % begin german
        \iftubsthesis@customtype % begin custom type (overwritten)
            \subtitle{\thesistype}
        \else % end custom type (overwritten) / begin not overwritten
            \subtitle{Exposé zur \thesistype}
        \fi % end no overwritten type
    \else % end german / begin english
        \iftubsthesis@customtype % begin custom type (overwritten)
            \subtitle{\thesistype}
        \else % end custom type (overwritten) / begin not overwritten
            \subtitle{\thesistype~Proposal}
        \fi % end no overwritten type
    \fi % end english
\else % end proposal / begin thesis
    \subject{\thesistype}
\fi % end thesis

\logo{\tubsthesis@institutelogo}

\unless\ifclsproposal % begin thesis
    \unless\iftubsthesis@diss % begin not diss thesis
        \ifclsgerman % begin german
            \publishers{
                \textbf{\tubsthesis@institute\\
                \tubsthesis@professor}\\
                \vspace*{2em}
                Betreuer:\\
                \supervisorone
                \supervisortwo
                \supervisorthree
            }
        \else % end german / begin english
            \publishers{
                \textbf{\tubsthesis@institute\\
                \tubsthesis@professor}\\
                \vspace*{2em}
                \supervisorstring\\
                \supervisorone
                \supervisortwo
                \supervisorthree
            }
        \fi % end english
    \fi % end not diss thesis
\fi % end thesis

\ifclsproposal % begin proposal
    \ifclsnodate % begin nodate
        \date{}
    \else % end nodate / begin date
        \date{\DTMusedate{tubsthesis@begindate}}
    \fi % end date
\else % end proposal / begin thesis
    \ifclsnodate % begin nodate
        \date{}
    \else % end nodate / begin date
        \date{\tubsthesis@date}
    \fi % end date
    \frontmatter % roman page numbering
\fi % end thesis

\ifclsproposal
    {%
        \let\newpage\relax
        \maketitle[plain,logo=left]
    }
\else % end proposal / begin thesis
    \iftubsthesis@diss % begin dissertation
        \pagestyle{empty}
        \pagenumbering{roman}

        \maketitle[image,logo=left]

    \else % end dissertation / begin not diss thesis
        \maketitle
    \fi % end not diss thesis
\fi % end thesis

\ifclsproposal % begin proposal

\begin{table}[h]
    \centering
    \begin{tabularx}{\tubsthesis@tablewidth}{XX}
        \hline
        \ifclsgerman % begin german
            \ifextratitle
                Englischer Titel& \titleenglish         \\\hline
            \fi
            Anmeldedatum        & \DTMusedate{tubsthesis@begindate} \\\hline
            Matrikelnummer      & \matrikelnummer       \\\hline
            E-Mail              & \mail                 \\\hline
            Studiengang         & \studysubject         \\
        \else % end german / begin english
            \ifextratitle
                German title    & \titlegerman          \\\hline
            \fi
            Registration date   & \DTMusedate{tubsthesis@begindate} \\\hline
            Registration number & \matrikelnummer       \\\hline
            E-Mail              & \mail                 \\\hline
            Subject             & \studysubject         \\
        \fi % end english
    \end{tabularx}
\end{table}

\iftubsthesis@presentationpoints % begin presentation points
    \begin{center}
        \ifclsgerman % begin german
            \textlnum{Der Abschlussvortrag geht mit \presentationpoints~Credits in die Abschlussnote ein.}
        \else % end german / begin english
            \textlnum{The presentation contributes \presentationpoints~credit points to the final grade.}
        \fi % end english
    \end{center}
\fi % end presentation points

\else % end proposal / begin thesis

\cleardoublepage

\iftubsthesis@diss % begin dissertation
    \begin{otherlanguage}{ngerman} % begin printing in german for dates
    \begin{center}
        \ifclsgerman % begin german
            {\large \titlegerman}
        \else % end german / begin english
            {\large \titleenglish}
        \fi % end english

        \vspace{1cm}

        \ifthenelse{\boolean{tubsthesis@finalprint}}{Von der}{Der}\linebreak
        \tubsthesis@faculty \linebreak
        der Technischen Universität Carolo-Wilhelmina zu Braunschweig \linebreak

        \vspace{.5cm}

        zur Erlangung des Grades \tubsthesis@degreearticle\linebreak

        \textbf{\tubsthesis@degree}\linebreak

        \vspace{.5cm}

        \ifthenelse{\boolean{tubsthesis@finalprint}}{genehmigte}{vorgelegte}
        Dissertation\linebreak
        \iftubsthesis@cumulative % begin adding of "(kumulative Arbeit)"
            (kumulative Arbeit)
        \fi % end adding of "(kumulative Arbeit)"

        \vspace{.5cm}

        von\linebreak
        \name\linebreak
        geboren am \DTMusedate{tubsthesis@birthdate}\linebreak
        in \tubsthesis@birthplace\linebreak
    \end{center}

    \vspace{4cm}

    \begin{tabular}{p{5cm} l}
        Eingereicht am: & \tubsthesis@date \\
        Disputation am: & \DTMusedate{tubsthesis@disputationdate} \\
        1. Referent: & \tubsthesis@professor \\
        2. Referent: & \tubsthesis@professortwo \\
    \end{tabular}

    \vfill

    \begin{center}
        \tubsthesis@printyear
    \end{center}

    \end{otherlanguage} % end german printing

    \pagestyle{headings}

    \tubsthesis@posttitlecontent
\else % end dissertation / begin not diss thesis
    \tubsthesis@posttitlecontent

    % statement of originality
    \thispagestyle{plain} % no header
    \vspace*{7cm}
    \ifclsgerman % begin german
        \centerline{\bfseries Eidesstattliche Erklärung}
        \vspace*{1em}
        \noindent
        Ich erkläre hiermit an Eides statt, dass ich die vorliegende
        \thesistype~selbstständig
        verfasst sowie alle benutzten Quellen und Hilfsmittel
        vollständig angegeben habe und dass die Arbeit
        nicht bereits als Prüfungsarbeit vorgelegen hat.

        \par
        \bigskip\noindent Braunschweig, den \tubsthesis@date \par
    \else % end german / begin english
        \centerline{\bfseries Statement of Originality}
        \vspace*{1em}
        \noindent
        This thesis has been performed independently with the
        support of my supervisor/s.
        To the best of the author's knowledge,
        this thesis contains no material previously
        published or written by another person except where
        due reference is made in the text.

        \par
        \bigskip\noindent Braunschweig, \tubsthesis@date \par
    \fi % end english
    \vspace*{10mm}
    \hfill\hrulefill
\fi % end not diss thesis
\cleardoublepage

\unless\ifclsnoabstract % begin abstract
    \thispagestyle{plain} % no header
    \ifclsgerman % begin german
        \centerline{\bfseries Zusammenfassung}
        \vspace*{1em}
        \noindent
        \mainabstract

        \ifextraabstract % begin extra abstract
            \vspace*{5em}

            \begin{otherlanguage}{english}
                \centerline{\bfseries Abstract}
                \vspace*{1em}
                \noindent
                \extraabstract
            \end{otherlanguage}
        \fi % end extra abstract
    \else % end german / begin english
        \centerline{\bfseries Abstract}
        \vspace*{1em}
        \noindent
        \mainabstract

        % If german abstract was given
        \ifextraabstract % begin extra abstract
            \vspace*{5em}

            \begin{otherlanguage}{ngerman}
                \centerline{\bfseries Zusammenfassung}
                \vspace*{1em}
                \noindent
                \extraabstract
            \end{otherlanguage}
        \fi % end extra abstract
    \fi % end english
    \cleardoublepage
\fi % end abstract

\ifincludedproposal % begin including proposal
    \tubsthesis@includedproposal
\fi % end including proposal

\tableofcontents
\cleardoublepage

\unless\ifclsnolistoffigures % begin listoffigures
    \listoffigures
    \cleardoublepage
\fi % end listoffigures

\unless\ifclsnolistoftables % begin listoftables
    \listoftables
    \cleardoublepage
\fi % end listoftables

\mainmatter

\fi % end thesis
}{%
\ifclsproposal % begin proposal
\noindent
\newpage
\ifclsgerman % begin german
    \chapter{Durchführung und Bearbeitung}
    Dieses Dokument stellt die Grundlage zur Bearbeitung
    der \thesistype~dar und beschreibt
    die vorgesehenen Inhalte und Ziele.
    Alle Hinweise und Vorschriften des betreuenden Instituts,
    der Fakultät und der TU Braunschweig werden beachtet.
Die Laufzeit beträgt \duration~Monate.
\vspace*{10mm}
\paragraph{Aufgabenstellung und Betreuung}\hfill\\[3ex]
\noindent
\begin{tabularx}{\textwidth}{@{}XX}
\supervisoronesign
\supervisortwosign
\supervisorthreesign
\tubsthesis@professor          & \rule[-0.5ex]{\linewidth}{1pt}\newline\itshape(\signature)
\end{tabularx}
\vspace*{10mm}
\paragraph{Bearbeitung}\hfill\\[3ex]
\noindent
\begin{tabularx}{\textwidth}{@{}XX}
\name       & \rule[-0.5ex]{\linewidth}{1pt}\newline\itshape(\signature)
\end{tabularx}
\else % end german / begin english
    \chapter{Execution and Editing}
    This document is the foundation for the \thesistype~and
    explains the designated contents and goals.
    All instructions and regulations of the supervising institute,
    the faculty and the TU Braunschweig are observed.
The duration of the thesis is \duration~months.
\paragraph{Task Definition and Supervision}\hfill\\[3ex]
\noindent
\begin{tabularx}{\textwidth}{@{}XX}
\supervisoronesign
\supervisortwosign
\supervisorthreesign
\tubsthesis@professor          & \rule[-0.5ex]{\linewidth}{1pt}\newline\itshape(\signature)
\end{tabularx}
\vspace*{10mm}
\paragraph{Task Execution}\hfill\\[3ex]
\noindent
\begin{tabularx}{\textwidth}{@{}XX}
\name       & \rule[-0.5ex]{\linewidth}{1pt}\newline\itshape(\signature)
\end{tabularx}
\fi % end english
\newpage
\fi % end proposal

\printbibliography

\unless\ifclsproposal % begin thesis

    \unless\ifclsnoappendix % begin appendix
        \appendix
    \fi % end appendix
\fi % end thesis
}
\endinput
%%
%% End of file `tubsthesis.cls'.
