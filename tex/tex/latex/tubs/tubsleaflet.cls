%%
%% This is file `tubsleaflet.cls',
%% generated with the docstrip utility.
%%
%% The original source files were:
%%
%% ../tubsvers.inc  (with options: `default,extra')
%% tubsdoc.dtx  (with options: `class,leaflet,head')
%% tubsdoc.dtx  (with options: `class,leaflet,option')
%% tubsfont.dtx  (with options: `class,leaflet,option')
%% tubshead.dtx  (with options: `class,leaflet,option')
%% tubsdoc.dtx  (with options: `class,leaflet,execoption')
%% tubsdoc.dtx  (with options: `class,leaflet,body')
%% tubsfont.dtx  (with options: `class,leaflet,body')
%% tubshead.dtx  (with options: `class,leaflet,body')
%% 
%% This is a generated file.
%% 
%% Copyright (C) 2011 by Enrico Jörns
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
\RequirePackage{ifthen}
\newcommand*{\tubsClassName}{%
 tubsleaflet%
}
\newcommand*{\BaseClass}{%
 leaflet%
}
\NeedsTeXFormat{LaTeX2e}[1999/12/01]
\ProvidesClass{\tubsClassName}[\tubslatexVersion\space document class (\BaseClass)]
\newcommand*{\@fsfbs@sub}{}
\RequirePackage{xkeyval}%
\DeclareOptionX{mono}{%
  \PassOptionsToPackage{mono}{tubslogo}
  \PassOptionsToPackage{mono}{tubsflowfram}
}
\DeclareOptionX{cmyk}{%
  \PassOptionsToPackage{cmyk}{tubscolors}
  \PassOptionsToPackage{cmyk}{tubslogo}
}
\DeclareOptionX{rgb}{%
  \PassOptionsToPackage{rgb}{tubscolors}
  \PassOptionsToPackage{rgb}{tubslogo}
}
\DeclareOptionX{landscape}{%
  \PassOptionsToPackage{landscape}{tubstypearea}
  \PassOptionsToClass{landscape}{\BaseClass}
}
\DeclareOptionX{paperwidth}{%
  \PassOptionsToPackage{paperwidth=#1}{tubstypearea}
}
\DeclareOptionX{paperheight}{%
  \PassOptionsToPackage{paperheight=#1}{tubstypearea}
}
\DeclareOptionX{oneside}{%
\setkeys{\tubsClassName.cls}{twoside=false}
}
\DeclareOptionX{marginleft}{%
  \PassOptionsToPackage{marginleft}{tubstypearea}
}
\DeclareOptionX{marginright}{%
  \PassOptionsToPackage{marginright}{tubstypearea}
}
\DeclareOptionX{extramargin}{%
  \PassOptionsToPackage{extramargin}{tubstypearea}
}
\DeclareOptionX{bcor}{%
  \PassOptionsToPackage{bcor=#1}{tubstypearea}
}
\def\tubs@opt@paper{}
\newcommand{\@fsfb@prefix}{}
\DeclareOptionX{a6paper}{%
  \def\tubs@opt@paper{a6paper}
}
\DeclareOptionX{langpaper}{%
  \renewcommand{\@fsfb@prefix}{tubslang}
  \PassOptionsToClass{fontsize=9pt}{\BaseClass}
  \PassOptionsToPackage{fontsize=9pt}{scrextend}
  \def\tubs@opt@paper{langpaper}
}
\DeclareOptionX{a5paper}{%
  \renewcommand{\@fsfb@prefix}{tubsa5}
  \PassOptionsToClass{fontsize=9pt}{\BaseClass}
  \def\tubs@opt@paper{a5paper}
}
\DeclareOptionX{a4paper}{%
  \renewcommand{\@fsfb@prefix}{tubsa4}
  \PassOptionsToClass{fontsize=11pt}{\BaseClass}
  \PassOptionsToPackage{fontsize=11pt}{scrextend}
  \def\tubs@opt@paper{a4paper}
}
\DeclareOptionX{a3paper}{%
  \renewcommand{\@fsfb@prefix}{tubsa3}
  \PassOptionsToClass{fontsize=13pt}{\BaseClass}
  \PassOptionsToPackage{fontsize=13pt}{scrextend}
  \def\tubs@opt@paper{a3paper}
}
\DeclareOptionX{a2paper}{%
  \renewcommand{\@fsfb@prefix}{tubsa2}
  \PassOptionsToClass{fontsize=18pt}{\BaseClass}
  \def\tubs@opt@paper{a2paper}
}
\DeclareOptionX{a1paper}{%
  \renewcommand{\@fsfb@prefix}{tubsa1}
  \PassOptionsToClass{fontsize=25pt}{\BaseClass}
  \def\tubs@opt@paper{a1paper}
}
\DeclareOptionX{a0paper}{%
  \renewcommand{\@fsfb@prefix}{tubsa0}
  \PassOptionsToClass{fontsize=40pt}{\BaseClass}
  \def\tubs@opt@paper{a0paper}
}
\DeclareOptionX{backend}{%
  \if#1{flow}
    \def\tubs@opt@backend{flowfram}
  \fi
  \ifx#1{pgf}
    \def\tubs@opt@backend{pgf}
  \fi
  \ifthenelse{\equal{#1}{base}}{%
    \def\tubs@opt@backend{base}
  }{}
  \ifthenelse{\equal{#1}{flow}}{%
    \def\tubs@opt@backend{flowfram}
  }{}
  \ifthenelse{\equal{#1}{pgf}}{%
    \def\tubs@opt@backend{pgf}
  }{}
}
\def\tubsleaflet@style{none}
\DeclareOptionX{style}[none]{%
  \def\tubsleaflet@style{#1}%
}
\DeclareOptionX{sender}{%
  \PassOptionsToPackage{sender=#1}{tubstypearea}
}
\DeclareOptionX{hyperref}{%
  \PassOptionsToPackage{%
    colorlinks,
    linkcolor=tuRed,
    anchorcolor=tuBlack,
    citecolor=tuGreenDark80,
    filecolor=tuBlue80,
    menucolor=tuRed,
    urlcolor=tuVioletLight
  }{hyperref}
}
\DeclareOptionX{hyperrefdark}{%
  \PassOptionsToPackage{%
    colorlinks,
    linkcolor=tuRed100,
    anchorcolor=tuBlack,
    citecolor=tuGreenDark,
    filecolor=tuBlueDark,
    menucolor=tuRed100,
    urlcolor=tuViolet
  }{hyperref}
}
\DeclareOptionX*{%
  \PassOptionsToClass{\CurrentOption}{\BaseClass}
}
\newcommand\tubs@fontsize{11pt}
\DeclareOptionX{fontsize}{%
  \renewcommand\tubs@fontsize{#1}
}
\newcommand\headingscolor{tuBlack}
\newcommand\tubs@fontcolor[1]{}
\DeclareOptionX{colorheadings}[tuSecondary]{%
  \renewcommand\headingscolor{#1}
  \renewcommand\tubs@fontcolor[1]{\color{#1}}
}
\newif\if@tubs@tf@smallchap\@tubs@tf@smallchapfalse
\DeclareOptionX{smallchapters}{%
  \@tubs@tf@smallchaptrue
}

\newif\iftubs@bottomsender\tubs@bottomsenderfalse
\define@choicekey{\tubsClassName.cls}{sender}[\val\nr]{top,bottom}{%
  \ifcase\nr\relax
    \tubs@bottomsenderfalse
  \or
    \tubs@bottomsendertrue
  \fi
}
\ExecuteOptionsX{langpaper,cmyk}
\ProcessOptionsX*\relax
\providecommand{\@fontsizefilebase}{}
\renewcommand{\@fontsizefilebase}{\@fsfb@prefix\@fsfbs@sub}
\PassOptionsToClass{DIV=1}{\BaseClass}
\LoadClass{\BaseClass}
\RequirePackage{tubscolors}
\RequirePackage{tubstypearea}
\RequirePackage{tubslogo}
\RequirePackage{tubsstyle}
\renewcommand*\foldmarkrule{.3mm}
\renewcommand*\foldmarklength{5mm}
\ifthenelse{\equal{\tubsleaflet@style}{simple}}{%
  \AddToBackground{1}{\tubs@topline\tubs@tubslogo[left]}
  \AddToBackground{6}{\tubs@topline\tubs@tubslogo[right,plain]}
}{\ifthenelse{\equal{\tubsleaflet@style}{none}}{%
  \relax
}{%
  \ClassError{tubsleaflet.cls}{%
    Invalid parameter for option 'style'
  }{%
    Allowed parameters: 'simple', 'none'
  }
}}
\RequirePackage{nexus}
\RequirePackage{xcolor}
\colorlet{tubsheadings}{\headingscolor}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newcommand\newtubsfont[3][\relax]{%
  \@ifundefined{scr@fnt@#2}{%
    \newkomafont[#1]{#2}{#3}%
  }{%
    \setkomafont{#2}{#3}%
  }%
}
\newcommand*\addtotubsfont[2]{%
  \@ifundefined{scr@fnt@#1}{}{%
    \addtokomafont{#1}{#2}%
  }%
}
\let\settubsfont\newtubsfont
\let\usetubsfont\usekomafont
\let\sectfont\relax
\@ifundefined{KOMAClassName}{% skip for latex classes
  \RequirePackage{scrbase}
  \RequirePackage{scrextend}
}{%
\newcommand\@loadkomafont[1]{
  \expandafter\@defaultunits\expandafter\@tempdima#1 pt\relax\@nnil
  \edef\@tempa{#1}%
  \setlength{\@tempdimb}{\@tempdima}%
  \edef\@tempb{\strip@pt\@tempdimb}%
  \addtolength{\@tempdimb}{-10\p@}%
  \edef\@ptsize{\strip@pt\@tempdimb}%
  \edef\@tempa{%
    \noexpand\makeatletter
    \noexpand\InputIfFileExists{\@fontsizefilebase\@tempa.clo}{%
      \noexpand\ClassInfo{\KOMAClassName}{%
        File `\@fontsizefilebase\@tempa.clo' used to setup font sizes}%
    }{%
      \noexpand\InputIfFileExists{\@fontsizefilebase\@tempb pt.clo}{%
        \noexpand\ClassInfo{\KOMAClassName}{%
          File `\@fontsizefilebase\@tempb pt.clo' used instead of%
          \noexpand\MessageBreak
          file `\@fontsizefilebase\@tempa.clo' to setup font sizes}%
      }{%
        \noexpand\changefontsizes{#1}%
      }%
    }%
    \noexpand\catcode`\noexpand\@=\the\catcode`\@
  }%
  \@tempa
}
\global\let\Huge\relax
\global\let\huge\relax
\global\let\LARGE\realx
\global\let\Large\relax
\global\let\large\relax
\global\let\normalsize\relax
\global\let\small\relax
\global\let\footnotesize\relax
\global\let\scriptsize\relax
\@loadkomafont{\tubs@fontsize}
}
\newtubsfont{intro}{}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newtubsfont{absheadline}{\sffamily\bfseries}
\newtubsfont{title}{\usekomafont{absheadline}\Huge}
\newtubsfont{headline}{\usekomafont{title}\tubs@fontcolor{tubsheadings}}
\newtubsfont{headlinesmall}{\usekomafont{absheadline}\huge\tubs@fontcolor{tubsheadings}}
\newtubsfont{subtitle}{\usekomafont{absheadline}\Large}
\newtubsfont{subheadline}{\usekomafont{subtitle}\tubs@fontcolor{tubsheadings}}
\newtubsfont{subheadlinesmall}{\usekomafont{absheadline}\large\tubs@fontcolor{
tubsheadings}}
\newtubsfont{author}{\sffamily\LARGE}
\newtubsfont{date}{\large}
\newtubsfont{institute}{\sffamily\fontsize{10pt}{12}\bfseries\selectfont}
\newtubsfont{infotext}{\large}
\newtubsfont{infotextitem}{\large}
\newtubsfont{copytext}{\normalsize}
\newtubsfont{caption}{\small}
\settubsfont{pageheadfoot}{\normalfont\mdseries\scshape}
\settubsfont{pagenumber}{\usekomafont{pagehead}\lnum}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\deffootnotemark{\lnum\textsuperscript{\thefootnotemark}}
\addtotubsfont{footnote}{\lnum}% TODO (see above)
\preto\labelenumi{\lnum}
\preto\labelenumii{\lnum}
\preto\labelenumiii{\lnum}
\providecommand*{\partformat}{\partname~\lnum\thepart\autodot}
\providecommand*\@seccntformat[1]{}%
\providecommand*{\othersectionlevelsformat}[3]{#3\enskip} % HERE!
\renewcommand*\@seccntformat[1]{%
   \protect\othersectionlevelsformat{#1}{%
     \expandafter\aftergroup\noexpand\@gobble}{\protect\lnum\csname the#1\endcsname}%
}
\providecommand*\sectionmarkformat{}%
\renewcommand*\sectionmarkformat{{\protect\lnum\thesection\autodot\enskip}}%
\providecommand*\figureformat{}%
\renewcommand*{\figureformat}{%
  \figurename~\lnum\thefigure%
  \autodot%
}
\providecommand*\tableformat{}%
\renewcommand*{\tableformat}{%
  \tablename~\lnum\thetable%
  \autodot%
}
\providecommand*\numberline@prefix{}%
\renewcommand*{\numberline@prefix}{\lnum}%
\AfterPackage{listings}{%
  \AtBeginDocument{%
    \def\fnum@lstlisting{%
    \lstlistingname
    \ifx\lst@@caption\@empty\else~\lnum\thelstlisting\fi}%
  }%
  \let\@orig@lst@numberstyle\lst@numberstyle
  \lst@AddToHook{Init}{%
    \l@addto@macro\lst@numberstyle\lnum
  }%
}%
\preto\@tabular{\lnum}
\preto\LT@array{\lnum}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newtubsfont{section}{\usekomafont{subheadline}}
\newtubsfont{subsection}{\usekomafont{subheadlinesmall}}
\addtotubsfont{subsubsection}{\tubs@fontcolor{tubsheadings}}
\newtubsfont{intro}{\large\tubs@fontcolor{tubsheadings}}%TODO: mdseries???
\renewcommand{\labelitemi}{\rule[0.1em]{0.4em}{0.4em}}
\renewcommand{\labelitemii}{\rule[0.1em]{0.3em}{0.3em}}
\parindent0mm
\parskip\medskipamount
\newcommand\@sec@cmd[2]{{\raggedsection\usekomafont{#1}#2\par}}
\define@boolkey{sec@cmd}{small}[true]{}%
\let\headline\@undefined
\newcommand\headline[2][]{%
  \setkeys{sec@cmd}{small=false,#1}%
  \ifKV@sec@cmd@small
    \@sec@cmd{headlinesmall}{#2}%
  \else
    \@sec@cmd{headline}{#2}%
  \fi
}
\let\subheadline\@undefined
\newcommand\subheadline[2][]{%
  \setkeys{sec@cmd}{small=false,#1}%
  \ifKV@sec@cmd@small
    \@sec@cmd{subheadlinesmall}{#2}%
  \else
    \@sec@cmd{subheadline}{#2}%
  \fi
}
\PassOptionsToPackage{olines}{scrlayer-scrpage}
\RequirePackage{scrlayer-scrpage}
\AtBeginDocument{\pagestyle{scrheadings}}
\newcommand\headsepline{\rule{25pt}{1pt}}
\providecommand*{\Ifthispageodd}{\ifthispageodd}%
\newcommand{\innerhead}[2][]{%
  % Benutze optionale Einstellung für linke Seite, falls vorhanden
  \def\@tubs@linnerh{#2}%
  \ifx#1\relax%
    \let\@tubs@rinnerh\@tubs@linnerh%
  \else%
    \def\@tubs@rinnerh{#1}%
  \fi%
  %
  \ifthenelse{\equal{#2}{}}{%
    \let\@iheadsepline\relax%
  }{%
    \let\@iheadsepline\headsepline%
  }%
  \iftubs@bottomsender\else%
    \newdimen\@tubs@headheight%
    \setlength\@tubs@headheight{\headheight}%
    \addtolength\@tubs@headheight{-2pt}%
    % Set left inner head
    \lohead{%
      \vtop to\@tubs@headheight{%
        \boxmaxdepth=0pt%
        \strut{\vbox to 4ex{}}%
        \@tubs@linnerh%
        \vfil%
      }%
    }%
    % Set right inner head
    \rehead{%
      \vtop to\@tubs@headheight{%
        \boxmaxdepth=0pt%
        \strut{\vbox to 4ex{}}%
        \@tubs@rinnerh%
        \vfil%
      }%
    }
  \fi%
}
\newcommand{\innerfoot}[2][]{%
  % Benutze optionale Einstellung für linke Seite, falls vorhanden
  \def\@tubs@linnerf{#2}%
  \ifx#1\relax%
    \let\@tubs@rinnerf\@tubs@linnerf%
  \else%
    \def\@tubs@rinnerf{#1}%
  \fi%
  %
  \ifthenelse{\equal{#2}{}}{%
    \let\@iheadsepline\relax%
  }{%
    \let\@iheadsepline\headsepline%
  }%
  \iftubs@bottomsender%
    % Set left inner foot
    \lofoot{%
      \raisebox{\tubspage@headheight+\depth}{%
        \vbox to\tubspage@headheight{%
          \vfill\vspace*{1ex}\strut%
          \@tubs@linnerf
          \vspace*{-1.5ex}\linebreak%
          \@iheadsepline\vspace*{1ex}%
        }%
      }%
    }%
    % Set right inner foot
    \refoot{%
      \raisebox{\tubspage@headheight+\depth}{%
        \vbox to\tubspage@headheight{%
          \vfill\vspace*{1ex}\strut%
          \@tubs@rinnerf
          \vspace*{-1.5ex}\linebreak%
          \@iheadsepline\vspace*{1ex}%
        }%
      }%
    }%
  \else\fi%
}
\newcommand{\innersender}[2][]{%
  \iftubs@bottomsender%
    \innerfoot[#1]{#2}%
  \else%
    \innerhead[#1]{#2}%
  \fi%
}
\newcommand{\outerhead}[2][\relax]{%
  % Benutze optionale Einstellung für linke Seite, falls vorhanden
  \def\@tubs@routerh{#2}%
  \ifx#1\relax%
    \let\@tubs@louterh\@tubs@routerh%
  \else%
    \def\@tubs@louterh{#1}%
  \fi%
  %
  \ifthenelse{\equal{#2}{}}{%
    \let\@oheadsepline\relax%
  }{%
    \let\@oheadsepline\headsepline%
  }%
  \iftubs@bottomsender\else%
    \newdimen\@tubs@headheight%
    \setlength\@tubs@headheight{\headheight}%
    \addtolength\@tubs@headheight{-\sls@headabove@linethickness}
    \addtolength\@tubs@headheight{-1pt}
    % Set left outer head
    \lehead{%
      \vtop to\@tubs@headheight{%
        \boxmaxdepth=0pt%
        \strut{\vbox to 4ex{}}%
        \@tubs@louterh
        \vfil%
      }%
    }
    % Set right outer head
    \rohead{%
      \vtop to\@tubs@headheight{%
        \boxmaxdepth=0pt%
        \strut{\vbox to 4ex{}}%
        \@tubs@routerh
        \vfil%
      }%
    }
  \fi%
}%
\newcommand{\outerfoot}[2][]{%
  % Benutze optionale Einstellung für linke Seite, falls vorhanden
  \def\@tubs@routerf{#2}%
  \ifx#1\relax%
    \let\@tubs@louterf\@tubs@routerf%
  \else%
    \def\@tubs@louterf{#1}%
  \fi%
  %
  \ifthenelse{\equal{#2}{}}{%
    \let\@oheadsepline\relax%
  }{%
    \let\@oheadsepline\headsepline%
  }%
  \iftubs@bottomsender%
  % Set left outer foot
  \lefoot{%
    \raisebox{\tubspage@headheight+\depth}{%
      \vbox to\tubspage@headheight{%
        \vfill\vspace*{\baselineskip}\strut%
        \@tubs@louterf
        \vspace*{-1.5ex}\linebreak%
        \@oheadsepline\vspace*{1ex}%
      }%
    }%
  }%
  % Set right outer foot
  \rofoot{%
    \raisebox{\tubspage@headheight+\depth}{%
      \vbox to\tubspage@headheight{%
        \vfill\vspace*{\baselineskip}\strut%
        \@tubs@routerf
        \vspace*{-1.5ex}\linebreak%
        \@oheadsepline\vspace*{1ex}%
      }%
    }%
  }%
  \else\fi%
}
\newcommand{\outersender}[2][]{%
  \iftubs@bottomsender%
    \outerfoot[#1]{#2}%
  \else%
    \outerhead[#1]{#2}%
  \fi%
}
\clearscrheadings
\clearscrplain
\setheadwidth[-1in-\hoffset-\oddsidemargin+\tubspage@bcor+2\tubsborderwidth]{\paperwidth-4\tubsborderwidth-\tubspage@bcor}
\iftubs@bottomsender\else%
  \ifthenelse{\isundefined{\KOMAoptions}}{%
    \setheadtopline[\tubsborderwidth]{1pt}[]
  }{%
    \KOMAoptions{headtopline=1pt:\tubsborderwidth}
  }
\fi%
\if@twoside % begin twoside
  \innersender[\leftmark]{\rightmark}
\else % end twoside / begin oneside
  \innersender[\leftmark]{\leftmark}
\fi % end oneside
\outersender[\pagemark]{\pagemark}
\newcommand{\cleartubsheadings}{%
  \innersender{}\innerfoot{}\outerhead{}\outerfoot{}%
}
\newpagestyle{@tubsheadings}
{%
  {%
    \rlap{\parbox{\@headwidth}{\raggedright
        \strut\tubsheadings@even@left@head\strut}}%
    \hfill
    \llap{\parbox{\@headwidth}{\raggedleft%
        \strut\tubsheadings@even@right@head\strut}}}%
  {%
    \rlap{\parbox{\@headwidth}{\raggedright
        \strut\tubsheadings@odd@left@head\strut}}%
    \hfill
    \llap{\parbox{\@headwidth}{\raggedleft%
        \strut\tubsheadings@odd@right@head\strut}}}%
  {%
    \rlap{\parbox{\@headwidth}{\raggedright
        \strut\tubsheadings@odd@left@head\strut}}%
    \hfill
    \llap{\parbox{\@headwidth}{\raggedleft
        \strut\tubsheadings@odd@right@head\strut}}}}%
{%
  {%
    \rlap{\parbox{\@footwidth}{\raggedright
        \strut\tubsheadings@even@left@foot\strut}}%
    \hfill
    \parbox{\@footwidth}{\centering
      \strut\tubsheadings@even@middle@foot\strut}%
    \hfill
    \llap{\parbox{\@footwidth}{\raggedleft
        \strut\tubsheadings@even@right@foot\strut}}}%
  {%
    \rlap{\parbox{\@footwidth}{\raggedright
        \strut\tubsheadings@odd@left@foot\strut}}%
    \hfill
    \parbox{\@footwidth}{\centering
      \strut\tubsheadings@odd@middle@foot\strut}%
    \hfill
    \llap{\parbox{\@footwidth}{\raggedleft
        \strut\tubsheadings@odd@right@foot\strut}}}%
  {%
    \rlap{\parbox{\@footwidth}{\raggedright
        \strut\tubsheadings@odd@left@foot\strut}}%
    \hfill
    \parbox{\@footwidth}{\centering
      \strut\tubsheadings@odd@middle@foot\strut}%
    \hfill
    \llap{\parbox{\@footwidth}{\raggedleft
        \strut\tubsheadings@odd@right@foot\strut}}%
  }%
}
\endinput
%%
%% End of file `tubsleaflet.cls'.
